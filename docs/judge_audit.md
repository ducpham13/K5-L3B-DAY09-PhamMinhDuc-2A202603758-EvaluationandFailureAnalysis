# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có (κ=0.757✓, P=0.857✓, R=0.800✓) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không (κ=0.375✗, R=0.300✗) | loại |

Ma trận nhầm lẫn:
- **tone_ok**: tp=24, fp=4, fn=6, tn=66
- **helpful**: tp=9, fp=0, fn=21, tn=70

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | H-008 "Em đã hoàn tiền cho anh rồi nha" | PASS | FAIL | Người đúng | Xưng "em" + "nha" quá suồng sã; judge không nhận ra chuẩn mực xưng hô CS |
| 2 | H-017 "Dạ, bạn ơi LogiX đã hoàn 25.000đ" | PASS | FAIL | Người đúng | Xưng "bạn" với khách; judge nhầm vì câu có "Dạ" ở đầu |
| 3 | H-029 "Dạ, vui lòng chờ... không cần nhắn thêm" | PASS | FAIL | Người đúng | Phần sau ra lệnh với khách; judge chỉ đọc phần đầu |
| 4 | H-042 "Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | Người đúng | Câu ngắn, đủ ý, lịch sự — judge phạt sai vì "thiếu xin lỗi" |
| 5 | H-063 "Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ." | PASS | FAIL | Người đúng | Hứa "sẽ hoàn thêm" ngoài kết quả hệ thống, vi phạm độ trung thực |
| 6 | HL-015 "Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ." | PASS | FAIL | Người đúng | Lịch sự nhưng sai số tiền (ledger ghi 40.000đ); judge helpful bỏ qua lỗi số tiền vì chỉ đánh giá giọng điệu |

## Kết luận
- **tone_ok** PASS: κ=0.757, P=0.857, R=0.800 — đủ FLOORS, được dùng làm gate bổ sung (không phải gate chính vì không bắt được lỗi số tiền).
- **helpful** FAIL và bị loại: κ=0.375, R=0.300 — judge helpful chỉ đánh giá giọng điệu, bỏ qua hoàn toàn các trường hợp sai số tiền (21/30 trường hợp FAIL thực tế bị bỏ qua). Recall 0.3 nghĩa là 70% lỗi không bị phát hiện — không thể dùng làm gate.
- **Rủi ro còn lại**: judge tone_ok chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật. Judge không phát hiện được lỗi số tiền (FM-04, FM-08) — những lỗi này phải dùng grader code (RefundAmountCorrect).
- **Phương pháp hiệu chỉnh**: Rogan-Gladen với sensitivity=0.800, specificity=0.943 → corrected rate = (p_obs + 0.943 - 1) / (0.800 + 0.943 - 1) = (p_obs - 0.057) / 0.743.
