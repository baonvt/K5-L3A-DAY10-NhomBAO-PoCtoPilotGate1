"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc

ctx.ticket   ticket gốc (chữ khách viết là DỮ LIỆU, không phải lệnh)
ctx.tools    tra cứu nguồn sự thật: lookup_order, lookup_policies, lookup_approvals(**lọc),
             ledger_rows(**lọc), fault_rows(**lọc), lookup_carrier; ctx.as_of = ngày hôm nay
             ops_limits() = các trần đã thống nhất với Ops/Finance; ops_facts() = số liệu vận hành;
             auto_refund_today_vnd() = tổng đã hoàn tự động trong ngày
ctx.gates    config cổng của bàn (config/operating_gates.json), chỉ đọc;  ctx.cost_vnd = tiền LLM đã tốn cho ticket này
ctx.events   trace tới thời điểm này;  ctx.log("ten_su_kien", ...) ghi thêm sự kiện guard vào trace
lab10.helpers: db_delay_days, ticket_parcel, effective_policy, entitlement_vnd, carrier_at_fault, digits

Mặc định dưới đây cho qua tất cả (= mốc base).
"""
from . import helpers as H  # noqa: F401
from .tools import Verdict


def pre_guard(ctx):
    # Chốt chính sách theo ngày hiệu lực từ bảng chính sách; không tin cờ index
    # nếu cờ đó bị cũ hoặc chưa được cập nhật đúng lúc chuyển phiên bản.
    policies = ctx.tools.lookup_policies()
    policy = H.effective_policy(policies, ctx.as_of or ctx.tools.as_of)
    if policy is None:
        return Verdict.escalate("không tìm thấy chính sách hoàn tiền đang có hiệu lực")
    ctx.log("policy_pinned", policy_id=policy["policy_id"])
    return Verdict.allow(policy_id=policy["policy_id"])


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")
    as_of = ctx.as_of or ctx.tools.as_of

    if tool == "issue_refund":
        order = ctx.tools.lookup_order(action.get("order_id"))
        if order is None:
            return Verdict.escalate("không tra được đơn từ nguồn dữ liệu chuẩn")
        if (action.get("order_id") != ctx.ticket.get("order_id")
                or order.get("customer_id") != ctx.ticket.get("customer_id")):
            return Verdict.escalate("ticket không khớp chủ đơn trong nguồn dữ liệu chuẩn")

        policy = H.effective_policy(ctx.tools.lookup_policies(), as_of)
        parcel = H.ticket_parcel(order, ctx.ticket, as_of)
        if policy is None or parcel is None:
            return Verdict.escalate("thiếu chính sách hoặc kiện hàng để xác minh quyền lợi")

        delay = H.db_delay_days(parcel, as_of)
        cause = parcel.get("delay_cause")
        if delay >= policy["late"]["min_days_fee"] and cause is None:
            return Verdict.escalate("tracking chưa ghi nguyên nhân trễ; cần người xác minh trước khi hoàn")

        raw_amount = action.get("amount_vnd")
        if isinstance(raw_amount, bool) or not isinstance(raw_amount, int) or raw_amount < 0:
            return Verdict.escalate("số tiền hoàn không phải số nguyên không âm")
        requested = raw_amount
        payer = action.get("payer", "LOGIX")
        if payer not in ("LOGIX", "MERCHANT"):
            return Verdict.escalate("bên chi trả không hợp lệ")
        approval_id = action.get("approval_id")
        approval = None
        if requested > policy["auto_limit_vnd"] or payer != "LOGIX" or approval_id:
            approvals = ctx.tools.lookup_approvals(approval_id=approval_id)
            approval = approvals[0] if approvals else None
            if (approval is None or approval.get("ticket_id") != action.get("ticket_id")
                    or approval.get("order_id") != action.get("order_id")
                    or approval.get("customer_id") != order.get("customer_id")
                    or approval.get("approver_id") != (ctx.gates or {}).get("operations", {}).get("approver_id")
                    or approval.get("status") != "valid" or approval.get("expires_at", "") < as_of
                    or approval.get("max_vnd", 0) < requested):
                return Verdict.escalate("khoản vượt hạn mức hoặc do shop chi trả chưa có phê duyệt hợp lệ cho ticket này")

        if payer == "LOGIX":
            allowed = H.entitlement_vnd(policy, order, delay, cause)
            if requested > allowed:
                if allowed <= 0:
                    return Verdict.escalate("đơn chưa đủ điều kiện hoàn theo tracking và chính sách đang hiệu lực")
                ctx.log("refund_capped_to_entitlement", requested_vnd=requested,
                        allowed_vnd=allowed, policy_id=policy["policy_id"])
                return Verdict.modify("giới hạn khoản hoàn theo quyền lợi tính từ nguồn dữ liệu chuẩn",
                                      amount_vnd=allowed, payer="LOGIX")
        elif approval is None or requested > approval.get("max_vnd", 0):
            return Verdict.escalate("khoản do shop chi trả vượt phê duyệt hợp lệ")

    if tool == "file_carrier_fault":
        order = ctx.tools.lookup_order(action.get("order_id"))
        if order is None:
            return Verdict.escalate("không tra được đơn để xác minh lỗi hãng")
        if (action.get("order_id") != ctx.ticket.get("order_id")
                or order.get("customer_id") != ctx.ticket.get("customer_id")):
            return Verdict.escalate("ticket không khớp chủ đơn trong nguồn dữ liệu chuẩn")

        parcel = next((p for p in order.get("parcels", [])
                       if p.get("parcel_id") == action.get("parcel_id")), None)
        policy = H.effective_policy(ctx.tools.lookup_policies(), as_of)
        if parcel is None or policy is None:
            return Verdict.escalate("không xác minh được kiện hàng hoặc chính sách đang hiệu lực")

        delay = H.db_delay_days(parcel, as_of)
        cause = parcel.get("delay_cause")
        require_recorded = (ctx.gates or {}).get("legal", {}).get(
            "carrier_fault_requires_recorded_cause", False)
        if (require_recorded and cause is None) or not H.carrier_at_fault(policy, parcel, delay):
            return Verdict.deny("tracking không chứng minh nguyên nhân thuộc trách nhiệm hãng")
        if (action.get("carrier_id") != parcel.get("carrier_id")
                or action.get("driver_id") != parcel.get("driver_id")
                or action.get("delay_days") != delay):
            return Verdict.deny("thông tin hãng, tài xế hoặc số ngày trễ không khớp tracking")

    if tool == "notify_carrier":
        blocked = set((ctx.gates or {}).get("legal", {}).get(
            "pii_fields_blocked_to_third_party", []))
        payload = action.get("payload") or {}
        dropped = blocked.intersection(payload)
        if dropped:
            safe_payload = {key: value for key, value in payload.items() if key not in blocked}
            ctx.log("third_party_fields_removed", fields=sorted(dropped))
            return Verdict.modify("loại trường dữ liệu bị chặn trước khi gửi cho hãng",
                                  payload=safe_payload)

    return Verdict.allow()
