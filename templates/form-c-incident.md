# Phiếu C · Sự cố và quyết định v2 · Khối 3

**Bàn:** NhomBAO · **Thẻ đã bốc:** S1

## C0 · Nhật ký lần chạy vòng 2

| # | Mã lần chạy | Bộ · mốc | Đổi một thứ gì | pass_rate (CI 95%) | pass_k | Hoàn sai · lỗi hãng oan · PII | Tỉ lệ chuyển người | Kết luận |
|---|---|---|---|---|---:|---|---:|---|
| 1 | R-S1-prepared-20261118-210442-4fe294 | S1 · prepared | Nhận đúng S1; chỉ còn cổng vòng 1 | 0,75 [0,50–1,00] | 0,75 | 0đ · 0 · 0 | 0,375 | Chặn hoàn sai và lỗi hãng oan, nhưng còn hoàn thiếu 105.000đ và chưa đạt hai ngưỡng ký. |
| 2 | R-S1-after-20261118-204758-b76fea | S1 · after | Dùng tracking thay số ngày khách tự khai khi xử lý yêu cầu; thêm theo dõi tỷ lệ số ngày được ẩn | 1,00 [1,00–1,00] | 1,00 | 0đ · 0 · 0 | 0,125 | Hai lỗi S1-03/S1-07 hết; không có hoàn thiếu trong 40 lượt. |
| 3 | R-S1-after-20261118-210429-4fe294 | S1 · after | Chuyển người khi status và ngày giao trong tracking mâu thuẫn | 1,00 [1,00–1,00] | 1,00 | 0đ · 0 · 0 | 0,125 | Không làm đổi kết quả S1; thêm chốt an toàn cho dữ liệu không nhất quán. |
| 4 | R-base-after-20261118-210435-4fe294 | base · after | Kiểm hồi quy sau các cổng mới | 1,00 [1,00–1,00] | 1,00 | 0đ · 0 · 0 | 0,3077 | 65 lượt bộ nền đều đạt, không có ca mới hỏng. |

Report tự kiểm tra cuối: R-S1-grade-20261118-210442-4fe294. Các mã base, prepared, after trong report: R-S1-before-20261118-210442-4fe294, R-S1-prepared-20261118-210442-4fe294, R-S1-after-20261118-210443-4fe294.

---

## C1 · Câu 3.0 · Mốc prepared và đối chiếu pre-mortem

- Mã grade: R-S1-grade-20261118-210442-4fe294 · base: R-S1-before-20261118-210442-4fe294 · prepared: R-S1-prepared-20261118-210442-4fe294.
- Cổng vòng 1 giảm lỗi rõ: trên gói S1, hoàn sai giảm từ 985.000đ xuống 0đ; lỗi hãng oan từ 30 xuống 0. Tỉ lệ đạt tăng từ 0,3077 lên 0,75. Tuy vậy còn hoàn thiếu 105.000đ; S1-03 và S1-07 vẫn hỏng. Hai ngưỡng ký chưa đạt ở prepared: pass_rate 0,75 < 0,85 và pass_k 0,75 < 0,80.
- Không có trần vận hành/kinh doanh nào bị vượt ở prepared. ROI 0,34; chi phí 7.452đ/ticket so với làm tay 10.000đ; LLM cao nhất 766đ so với trần 1.500đ; tiền hoàn tự động 38.000đ so với trần bàn 1.500.000đ; hàng chờ không ùn.

**Bổ sung vòng 2 (đánh dấu khác màu trên bản giấy):** B6 đã nêu khách có thể khai sai số ngày, nhưng cổng vòng 1 chỉ chặn hoàn vượt quyền lợi và thiếu nguyên nhân; nó chưa loại số khách tự khai khỏi quyết định nên vẫn gây hoàn thiếu, và cổng ghi hãng từ chối cả số ngày bị model ghi sai. Rủi ro dữ liệu chưa được tính tới: parcel có status DELIVERED nhưng delivered_date trống. B3 còn ghi “ngày giao trống nghĩa là chưa giao”, giả định này không đúng với O-2120-P1 và O-2121-P1.

Sự cố nằm ở lăng kính kỹ thuật và dữ liệu; hậu quả chạm tới tiền và quan hệ pháp lý với hãng. Phần còn thiếu trong pre-mortem là kiểm tra tính nhất quán giữa status và ngày giao, và việc thiếu lịch sử lỗi hãng theo cửa sổ 7 ngày.

| Lý do thất bại đã xảy ra | Lăng kính | Kiểm được bằng gì |
|---|---|---|
| Model đã dùng số ngày khách tự khai để tính quyền lợi và đề xuất số ngày ghi lỗi hãng. | Kỹ thuật | S1-03@11, S1-07@11: model_override, tracking, proposal. |
| Dữ liệu đã để trạng thái DELIVERED đi cùng delivered_date trống; helper tính ngày đến as_of và không đọc status. | Dữ liệu | S1-20@11 và world_patch: O-2120-P1. |
| Chưa có lịch sử đối soát đủ 7 ngày để biết GHSH đã gần ngưỡng tạm ngưng tuyến hay chưa. | Vận hành / pháp lý | data/world.json có ngưỡng của GHSH nhưng không có sổ lỗi có timestamp 7 ngày. |

---

## C2 · Câu 3.1 · Bảng soát lỗi của thẻ

**Tác hại:** GHSH bị ghi lỗi/đối soát sai và khách nhận tiền sai; đo bằng số tiền hoàn, số lỗi hãng sai và pass_rate. Ở base S1: hoàn sai 985.000đ, hoàn thiếu 105.000đ, 30 lỗi hãng oan trên 65 lượt; pass_rate 0,3077.

### Phần 1 · Ghi lỗi

| # | Lỗi và bằng chứng | Ai gặp, ai chịu | Hệ trọng | Loại lỗi |
|---|---|---|---|---|
| 1 | S1-03@11: khách ghi 9 ngày; tracking ghi 4; model_override dùng 9; đề xuất 110.000đ thay vì 30.000đ. Cổng prepared cắt tiền về 30.000đ nhưng từ chối file_carrier_fault vì delay_days=9. | LogiX chịu khoản hoàn sai; GHSH nhận số ngày sai nếu lệnh lọt qua. | Cao | Lỗi chìm đối với hãng; hệ thống không nhận ra số ngày mình đã ghi là sai. |
| 2 | S1-07@11: khách ghi 2 ngày; tracking ghi 4; model_override dùng 2, trả lời từ chối và hoàn 0đ dù nhãn đúng là 21.000đ cùng lỗi VNX. | Khách bị thiếu quyền lợi và mất tin tưởng; CSKH phải nhận khiếu nại. | Cao | Giới hạn của hệ thống: model không giữ được tracking làm căn cứ khi số khách khác đi. |
| 3 | S1-20@11: O-2120-P1 có status DELIVERED, delivered_date null; helper tính 6 ngày từ promised_date đến as_of. Agent hoàn 22.000đ và ghi GHSH lỗi, trong khi nhãn yêu cầu chuyển người. | GHSH chịu lỗi không có căn cứ; LogiX trả tiền sai; khách có thể không biết dữ liệu mâu thuẫn. | Cao | Lỗi chìm do dữ liệu không nhất quán. |

### Phần 2 · Tìm nguồn

| Câu hỏi | Lỗi 1 | Lỗi 2 | Lỗi 3 |
|---|---|---|---|
| Đầu vào | Có: lời khách “9 ngày” lấn át tracking. | Có: lời khách “2 ngày” lấn át tracking theo chiều ngược lại. | Một phần: lời khách nói đã nhận hàng, nhưng dữ liệu parcel mâu thuẫn. |
| Độ liên quan / chất lượng dữ liệu | Tracking có đủ; agent không dùng làm nguồn cuối. | Tracking có đủ; agent không dùng làm nguồn cuối. | Có: delivered_date trống nhưng status báo đã giao; hàm tính ngày bỏ qua status. |
| Thứ bậc hệ thống | Không thấy hai hệ thống cùng ghi. | Không thấy hai hệ thống cùng ghi. | Chưa có nguồn dữ liệu đối soát nào giải quyết mâu thuẫn trạng thái và ngày. |
| Trạng thái hỏng | Không; lệnh vẫn chạy và có thể ghi sai âm thầm. | Không; hệ thống trả lời được nhưng sai quyền lợi. | Không; hệ thống tự hoàn tất thay vì dừng để xác minh. |

### Phần 3 · Hướng xử lý

| | Lỗi 1 | Lỗi 2 | Lỗi 3 |
|---|---|---|---|
| Vì sao người gặp coi đây là lỗi | Số ngày ghi cho hãng không khớp tracking, và số tiền hoàn không đúng chính sách. | Khách đủ điều kiện theo tracking nhưng bị từ chối. | Không thể lấy ngày hiện tại thay cho ngày giao thực tế khi hai trường dữ liệu mâu thuẫn. |
| Giải pháp | Ẩn số ngày khách tự khai trước khi model đọc; cổng ghi hãng đối chiếu parcel. | Model tính lại từ tracking sau khi claim bị ẩn; nếu thiếu dữ liệu thì chuyển người. | Tạm dừng ticket mâu thuẫn, người đối soát xác minh rồi mới hoàn/ghi lỗi. |
| Đường đi sau giải pháp | Tracking hợp lệ → tính lại → ghi lỗi đúng hãng, gửi payload đã bỏ trường bị chặn. | Tracking đủ → hoàn 21.000đ và ghi VNX đúng; thiếu thì vào hàng chờ. | Chuyển người; không hoàn và không ghi lỗi cho đến khi sửa nguồn. |
| Tín hiệu theo dõi | customer_delay_claim_redaction_rate; wrongful_carrier_faults. | customer_delay_claim_redaction_rate; pass_rate và under_refund_vnd. | wrongful_carrier_faults trong report; tracking_fields_inconsistent trong log để người đối soát xem. |

---

## C3 · Câu 3.1 · Phần riêng theo thẻ

Chỉ điền phần S1 yêu cầu là C3.5.

### C3.5 · Mở lại bản đồ dữ liệu: các trường của parcel

| Trường | Vòng 1 đã coi là | Sau khi đọc thẻ thì thấy | Ảnh hưởng tới tiền hoặc lỗi hãng |
|---|---|---|---|
| promised_date | Nguồn tracking chuẩn. | Vẫn là mốc hẹn cần đối chiếu; ngoài thực tế có thể bị nhập sai hoặc thay đổi mà không lưu lịch sử. | Nếu ngày hẹn sai thì mọi phép tính trễ lệch theo. |
| delivered_date | Nguồn tracking chuẩn; B3 ghi ngày trống nghĩa là chưa giao. | O-2120-P1 và O-2121-P1 có status DELIVERED nhưng ngày trống. H.db_delay_days thay ngày trống bằng as_of. | Có thể biến một bản ghi thiếu thành 6 hoặc 9 ngày trễ, rồi hoàn và ghi lỗi oan. |
| status | Có trong parcel nhưng chưa dùng làm điều kiện. | Helper db_delay_days không đọc status; status mâu thuẫn với ngày phải được coi là dữ liệu chưa xác minh. | Nếu bỏ qua status, không biết đã giao hay chưa và dễ tính sai quyền lợi. |
| delay_cause | Nguồn tracking; cổng vòng 1 yêu cầu nguyên nhân ghi nhận. | S1-21 để cause null; không thể quy lỗi hãng chỉ dựa vào số ngày. | Không có cause hợp lệ thì không ghi lỗi hãng; chuyển người. |
| parcel_id / carrier_id / driver_id | ID để chỉ đúng kiện và bên chịu trách nhiệm. | Cần khớp đúng kiện; đơn nhiều kiện có thể có hãng hoặc ngày giao khác nhau. | Sai ID có thể ghi lỗi cho nhầm hãng/tài xế. |

---

## C4 · Câu 3.1 · HAZOP của thẻ

Tool chọn phân tích: file_carrier_fault.

| Tham số / dòng dữ liệu | Guideword | Lệch cụ thể | Hậu quả, cho ai | Hiện có gì ngăn? | Gate đề xuất + tầng |
|---|---|---|---|---|---|
| delay_days đưa vào lệnh ghi | WRONG | S1-03@11: model dùng 9 ngày trong khi tracking là 4. | GHSH bị ghi số ngày sai; LogiX tính tiền theo số do model đề xuất. | Prepared đã chặn mức hoàn cao và từ chối ghi lỗi sai số, nhưng S1 vẫn hỏng. | Ẩn claim ở pre_guard; lấy delay từ tracking ở write_gate. Tầng chặn. |
| delivered_date và status của parcel | INCOMPLETE | O-2120-P1 có ngày giao null nhưng status DELIVERED; helper lấy as_of, ra 6 ngày. | Hoàn tiền và ghi lỗi không có dữ liệu giao nhất quán; hãng chịu rủi ro. | Ticket CT bị đưa ra ngoài phạm vi pilot, nhưng ở base agent vẫn tự xử lý. | pre_guard chuyển người nếu thiếu promised_date hoặc status/ngày giao mâu thuẫn. Tầng chặn. |
| số lỗi của cùng carrier trong ngày | PERTURBED | S1-40…S1-43 dồn trong cùng kịch bản; GHSH có ngưỡng tạm ngưng 3 lỗi/7 ngày, Ops đặt tối đa 2 lỗi tự động/carrier/ngày. | Nếu ghi tiếp lỗi thứ ba mà không kiểm lịch sử, tuyến có thể bị tạm ngưng và 12 tài xế bị ảnh hưởng. | Ops có giới hạn 2/ngày nhưng trước đây code chưa dùng nó. | write_gate đếm lỗi trong ngày; từ lần thứ ba chuyển người. Tầng vận hành/giới hạn thiệt hại. |

---

## C5 · Câu 3.2, 3.3 · Specification và giả định môi trường

### Specification

Trước khi hoàn tiền hoặc ghi lỗi hãng, hệ thống phải dùng đúng parcel; tính số ngày từ tracking; yêu cầu nguyên nhân được ghi; không hành động tự động khi status và delivered_date mâu thuẫn; không ghi tự động vượt giới hạn lỗi hãng trong ngày.

Kiểm bằng pre_guard và write_gate; đối chiếu wrongful_refund_vnd, under_refund_vnd, wrongful_carrier_faults, pass_rate trong report.

### Giả định môi trường có thể sai

Thiết kế giả định promised_date, delivered_date, status và delay_cause được cập nhật đầy đủ, nhất quán; hệ thống thật còn xem được sổ lỗi hãng có ngày giờ trong cửa sổ 7 ngày. S1-20 cho thấy ngày giao có thể thiếu dù status báo DELIVERED; kho mock không có lịch sử đủ 7 ngày để xác nhận GHSH đang có bao nhiêu lỗi.

---

## C6 · Câu 3.4 · Fault tree trước khi sửa

Mã lần chạy: R-S1-before-20261118-210442-4fe294.

    [ĐỈNH] GHSH bị ghi lỗi hoặc bị phạt oan; LogiX hoàn sai
    Đo bằng wrongful_carrier_faults và wrongful_refund_vnd
     └─ HOẶC
     ├─ [1] Model lấy số ngày khách tự khai làm số ngày ghi lỗi/hoàn tiền
     │    tầng: đầu vào · S1-03@11: ticket 9 ngày, tracking 4 ngày
     ├─ [2] Ngày giao thiếu nhưng agent vẫn tự tính đến as_of
     │    tầng: data · S1-20@11: DELIVERED, delivered_date null, delay 6
     └─ [3] Lỗi hãng dồn theo ngày, agent ghi tự động mà không kiểm ngưỡng
          tầng: hành động/quyền hạn · S1-40…S1-43 và ngưỡng GHSH 3 lỗi/7 ngày

| Lá | Specification bị vi phạm | Giả định môi trường đã sai |
|---|---|---|
| 1 | Số ngày dùng cho quyền lợi và file lỗi phải lấy từ tracking. | Khách ghi đúng số ngày và model sẽ phân biệt lời khai với dữ liệu chuẩn. |
| 2 | Ngày giao trống hoặc mâu thuẫn với status thì phải dừng để xác minh. | delivered_date luôn có nếu status là DELIVERED. |
| 3 | Không ghi tự động khi đã chạm giới hạn; cần tính cả cửa sổ hợp đồng. | Không có lỗi GHSH trước đó trong 7 ngày. |

---

## C7 · Câu 3.5 · Bảng sửa

| Nhánh | Nguyên nhân | Chỗ sửa | Tầng | Giảm hay ngăn? | Mã lần chạy |
|---|---|---|---|---|---|
| 1 | Model tin lời khai 9 ngày hoặc 2 ngày thay tracking. | guards.py: pre_guard ẩn số ngày tự khai; write_gate/file_carrier_fault chỉnh số ghi theo tracking đã xác minh. | Chặn | Ngăn dạng claim số đã nhận diện trong bộ thử; vẫn hở nếu tracking sai hoặc câu viết ngoài mẫu regex. | R-S1-after-20261118-204758-b76fea |
| 2 | Helper lấy as_of khi delivered_date trống và bỏ qua status. | guards.py: pre_guard chuyển người nếu ngày giao và status không nhất quán. | Chặn | Ngăn tự động xử lý trường hợp mâu thuẫn mà code nhận diện; chưa kiểm chứng trên tracking thật. | R-S1-after-20261118-204941-0e4328 |
| 3 | Chưa thực thi giới hạn lỗi hãng tự động của Ops. | guards.py: write_gate/file_carrier_fault đọc max_auto_strikes_per_carrier_per_day; khi đã có 2 lỗi thì chuyển người trước lệnh thứ ba. | Vận hành / giới hạn thiệt hại | Ngăn lỗi tự động thứ ba trong ngày của cùng hãng; không thay được việc kiểm sổ 7 ngày của GHSH. | R-S1-after-20261118-204758-b76fea |

---

## C8 · Câu 3.6 · Chỉ số theo dõi mới

| | Chỉ số của bàn |
|---|---|
| Tên trong MONITORS | customer_delay_claim_redaction_rate |
| Bước / hành vi được đo | Ticket có số ngày trễ do khách tự nêu và bị guard ẩn trước khi model đọc. |
| Thước đo | Tỉ lệ ticket trong một lượt đánh giá có ít nhất một claim số ngày được ẩn. |
| Dữ liệu | trial.events[].kind = customer_delay_claim_redacted; không đọc nhãn đúng/sai. |
| Cách tính | Số trial có sự kiện trên chia tổng trial; nếu danh sách rỗng thì mẫu số dùng 1 và kết quả là 0. |
| Khung thời gian / ngưỡng báo động | Một lượt đánh giá; khi áp dụng thật, tổng hợp theo ngày. Đề xuất vàng >0,25; đỏ >0,50 thì NV-TUNG/NV-HANH kiểm mẫu và xem xét dừng ghi lỗi tự động. |
| Điểm mù | Không phát hiện tracking sai, thiếu lịch sử 7 ngày hay claim viết bằng cách mà bộ lọc không nhận ra. |
| Giá trị bộ nền · S1 | Sau: 0,230769 · 0,625. Giá trị S1 cao hơn 0,394231 điểm; monitor sáng đèn. |

---

## C9 · Câu 3.7 · Fault tree sau khi sửa

Mã lần chạy: R-S1-after-20261118-210443-4fe294.

    [ĐỈNH] GHSH bị ghi lỗi hoặc bị phạt oan; LogiX hoàn sai
     └─ HOẶC
     ├─ [1] Claim số lọt qua VÀ pre_guard/write_gate không chặn được
     ├─ [2] Tracking sai hoặc mâu thuẫn VÀ pre_guard không nhận ra
     └─ [3] Đã có lỗi trong 7 ngày VÀ hệ thống không có lịch sử timestamp để biết trước lần ghi tiếp

| Nhánh | Gate | Tầng | Giảm hay ngăn? | Nhánh còn hở |
|---|---|---|---|---|
| 1 | pre_guard redaction; write_gate đối chiếu delay với tracking | Chặn | Ngăn dạng claim số đã nhận diện trong bộ thử; không bảo đảm với mọi cách diễn đạt. | Tracking nguồn sai hoặc claim không khớp mẫu. |
| 2 | pre_guard kiểm promised_date, delivered_date, status | Chặn | Chuyển người khi thấy thiếu ngày hoặc mâu thuẫn. | Dữ liệu sai nhưng các trường vẫn tự nhất quán. |
| 3 | write_gate đếm lỗi cùng carrier trong ngày; Ops giới hạn 2 | Vận hành | Chặn lần ghi tự động thứ ba trong cùng ngày. | Không đọc được lịch sử GHSH trong 7 ngày. |

---

## C10 · Câu 3.7 · Risk register

| Rủi ro | Khả năng | Tác động | PIC | Dấu hiệu | Xử lý | Ảnh hưởng bước đánh giá | Nhóm |
|---|---|---|---|---|---|---|---|
| Sổ 7 ngày của GHSH không có trong dữ liệu; số lỗi trong ngày có thể khác số lỗi dùng để tạm ngưng tuyến. | Chưa định lượng; S1 có 2 lỗi GHSH hợp lệ trong cụm HN/HCM, nhưng không biết lịch sử trước đó. | Lỗi thứ ba trong 7 ngày có thể làm ngưng tuyến; hợp đồng nêu phạt 150.000đ/lỗi và ảnh hưởng 12 tài xế. | NV-OANH | wrongful_carrier_faults > 0 thì dừng ngay; trước mỗi lỗi GHSH cần đối chiếu sổ 7 ngày. | NV-OANH lấy sổ có timestamp; nếu không xác minh được thì tắt file_carrier_fault cho GHSH và chuyển người. | Chưa mở rộng pilot cho đến khi có sổ đối soát thật và chạy lại cụm nhiều lỗi. | MEASURE / MANAGE |

---

## C11 · Câu 3.7 · Cập nhật checklist và Runbook phần 4–5

### Cập nhật checklist 9 nhóm việc

| # nhóm | Trạng thái mới | Bằng chứng | PIC |
|---|---|---|---|
| 1 · Chất lượng | Xong trên bộ nhìn thấy; còn chờ kiểm ẩn | Grade R-S1-grade-20261118-210442-4fe294: S1 pass 1,00; base pass 1,00; không có ca mới hỏng. | Nguyễn Võ Thái Bảo |
| 2 · Dữ liệu | Chưa | S1-20 có status/ngày giao mâu thuẫn; chưa có data thật và lịch sử GHSH 7 ngày. | Nguyễn Võ Thái Bảo |
| 3 · Bảo mật | Xong trong bộ thử | Trace S1-03 after bỏ customer_note; report pii_leaks = 0. | Nguyễn Võ Thái Bảo |
| 4 · Quyền hạn | Xong trong bộ thử | write_gate chỉ cho ghi theo tracking, và chuyển người trước lỗi tự động thứ ba trong ngày. | Nguyễn Võ Thái Bảo |
| 6 · Chi phí | Xong trong phạm vi | S1 after 4.994đ/ticket so với 10.000đ làm tay; ROI 1,00; LLM cao nhất 775đ. | Nguyễn Võ Thái Bảo |
| 7 · Vận hành | Chưa | Cần xác nhận sổ lỗi GHSH 7 ngày và người trực thực tế; runbook đã cập nhật ở dưới. | Nguyễn Võ Thái Bảo |
| 9 · Quyết định | Chưa chốt triển khai | Grade còn đỏ integrity do thiếu S2–S8 và máy không có test ẩn; cần Coach xác nhận hướng xử lý. | Nguyễn Võ Thái Bảo |

### Runbook 4 · Sau sự cố trên thẻ

| Câu hỏi | Trả lời |
|---|---|
| Tín hiệu ở Runbook 2 lẽ ra báo trước? | wrongful_carrier_faults > 0 và tỉ lệ notice bị sửa/thu hồi; trước sửa chưa có metric cho claim số ngày. Sau sửa, customer_delay_claim_redaction_rate là 0,625 trên S1. |
| Ngưỡng nào đổi? | Giữ giới hạn Ops tối đa 2 lỗi tự động/carrier/ngày; lần thứ ba phải chuyển người. Thêm kiểm tra sổ GHSH: khi đã có 2 lỗi trong 7 ngày thì NV-OANH đối soát trước lỗi tiếp theo vì hợp đồng dừng tuyến ở lỗi thứ ba. |
| Đổi gì về người? | Không tăng người trực thường kỳ vì hàng chờ sau là 0 phút. NV-OANH chịu trách nhiệm đối soát hãng; NV-HANH duyệt ca mâu thuẫn; NV-TUNG có quyền dừng nhận tự động. |
| Đổi gì về phạm vi/quy trình? | Giữ HN/HCM 100%; CT/DN tiếp tục làm tay. Trường status/ngày không khớp thì chuyển người. Tiếp tục kiểm lại 10% quyết định tự động. |
| Nói gì với bên thứ ba, ai, khi nào? | NV-OANH báo GHSH trước 17h cùng ngày, gửi danh sách mã đơn/kiện và số ngày đã đối chiếu; không gửi customer_note, số điện thoại hay địa chỉ. |
| Dữ liệu cá nhân nào đã rời hệ thống? | Report after ghi pii_leaks = 0; trace after bỏ customer_note trước khi gửi. Chưa có dữ liệu cá nhân nào cần thu hồi trong mốc này. |
| Phát hiện đầu tiên từ đâu? | Lời khiếu nại của GHSH và đọc trace, không phải monitor production. Nguồn còn thiếu là sổ lỗi có timestamp 7 ngày và xác nhận của người vận hành hãng. |

### Runbook 5 · Ba kịch bản tuần đầu

1. Nếu lượng ticket lên gấp 3 mức nền trong một giờ (khoảng 8,25 ticket/giờ) hoặc có từ 4 ca chờ: NV-TUNG gọi người dự phòng; nếu chờ quá 30 phút thì thu hẹp và chuyển ticket mới sang làm tay.
2. Nếu lỗi LLM/429 kéo dài quá 5 phút hoặc lặp lại 3 lần trong ca: dừng lệnh ghi tự động, chuyển ticket sang NV-HANH; NV-TUNG chỉ bật lại sau khi kiểm tra base và S1.
3. Nếu người duyệt không tin một quyết định: giữ ticket đó, đối chiếu tracking và policy; nếu phát hiện ghi sai tiền/lỗi hãng thì dừng tool tương ứng, báo NV-TUNG và NV-OANH ngay.

---

## C12 · Quyết định Gate 1 · v2

| | v2 |
|---|---|
| Commit ký tiêu chí | 515efae · hash 868767192b52 |
| Hash chốt cổng vòng 1 | bb2e08b7 |
| Mã lần chạy dùng làm bằng chứng | S1 base R-S1-before-20261118-210442-4fe294 · prepared R-S1-prepared-20261118-210442-4fe294 · after R-S1-after-20261118-210443-4fe294 |
| Còn dòng vượt trần? | Không. Không vượt chi phí, hàng chờ, ngân sách hoàn, pháp lý hay ROI. |
| Kho hoặc hãng xấu nhất | HCM có chi phí 2.071đ/ticket và review 0,3333; HN là 748đ/ticket và review 0. Cả hai pass 1,00, không hoàn sai hoặc lỗi hãng oan; riêng HCM vẫn thấp hơn làm tay 10.000đ nên không đổi phạm vi. GHSH có 35 lượt S1, pass 1,00, không lỗi hãng oan. |
| Quyết định | **Cải tiến thêm** trước khi chuyển sang pilot thật; giữ phạm vi dự kiến HN/HCM, chưa mở rộng. |
| Bằng chứng 1 | R-S1-after-20261118-210443-4fe294: pass_rate 1,00 và pass_k 1,00; wrongful/under-refund, wrongful_carrier_faults và PII đều 0. |
| Bằng chứng 2 | Cùng report: chi phí 4.994đ/ticket so với 10.000đ làm tay; ROI 1,00; tiền hoàn/ngày 38.000đ dưới trần 1.500.000đ; chờ lâu nhất 0 phút. |
| Bằng chứng 3 | R-base-after-20261118-210435-4fe294: 65/65 lượt đạt; không có ca mới hỏng. Monitor claim rate S1 0,625 so với base 0,230769. |
| Khớp decision_rule nào? | Các ngưỡng đã ký đều đạt nên có thể cân nhắc Tiếp tục trong phạm vi. Bàn vẫn chọn Cải tiến thêm vì grade tổng thể còn đỏ integrity do thiếu S2–S8, trái với README repo thẻ chỉ cho lấy S1; máy cũng không có test ẩn. Cần Coach xác nhận trước khi coi bài kiểm tra hoàn tất. |
| Nếu Cải tiến thêm | Coach xác nhận cách xử lý manifest S2–S8; chạy test ẩn; xác minh sổ GHSH có timestamp 7 ngày và thử dữ liệu status/date thật. |
| Ngày quyết định lại | 2026-11-25 hoặc ngay sau khi có phản hồi Coach và test ẩn. |
| PIC | Nguyễn Võ Thái Bảo · cần tự đọc lại và ký nếu nộp bản giấy. |

V2 đổi so với v1: v1 là tiếp tục HN/HCM theo bộ nền; S1 cho thấy prepared còn pass 0,75 và hoàn thiếu 105.000đ. Sau sửa, các chỉ số nhìn thấy đạt, nhưng integrity của grader chưa đạt nên chưa đề xuất triển khai thật. Report ghi “Được phép cân nhắc Tiếp tục”; quyết định Cải tiến thêm là do điều kiện kiểm thử và gói bài chưa được xác nhận, không phải vì ngưỡng kinh doanh còn đỏ.

**Một điều bộ thử chưa đo:** tính nhất quán của tracking thật và tổng lỗi GHSH trong 7 ngày. S1-20 ở CT ngoài scope nên guard mới chưa chạy trên ca đó; vì vậy giữ CT/DN ngoài pilot và không kết luận dữ liệu production đã an toàn.

**Ba dòng bắt buộc**

1. Giả định môi trường: tracking ghi đúng và kịp thời promised_date, delivered_date, status, delay_cause; giả định này có thể sai khi quét giao trễ hoặc bỏ sót.
2. Gate ngăn nhánh lấy số ngày khách tự khai thành căn cứ khi tracking nhất quán, nhưng chỉ giảm rủi ro tổng thể vì tracking có thể sai hoặc thiếu.
3. Trong pilot thật cần đối soát parcel-level các ngày hẹn/giao/trạng thái/nguyên nhân, sổ lỗi hãng 7 ngày, lỗi hoàn thiếu/sai, khiếu nại hãng, chi phí và thời gian chờ trước Bước đánh giá 2.
