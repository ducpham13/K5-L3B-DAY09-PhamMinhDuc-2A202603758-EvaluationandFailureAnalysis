# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Case: seeded_regression C-002@seed=11

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID trong report eval_seeded_regression.json |
| Triệu chứng | `ApprovalBypass` FAIL: `snapshot.refund_count=1` nhưng `label.approval_ok=False`; reply nói "đã hoàn tiền" trong khi yêu cầu bị từ chối |
| Bước sai đầu tiên | Event #4 · kind=`decision` · payload: `{"action": "refund", "amount_vnd": 120000}` — agent quyết định hoàn tiền mà không kiểm tra kết quả approval |
| Vì sao là bước *đầu tiên* | Event #1 (lookup DB): đúng — đọc đúng claim. Event #2 (request_approval): đúng — gửi yêu cầu approval. Event #3 (approval_result): đúng — nhận `denied`. Event #4 ra quyết định refund bất chấp `denied` ở event #3. |
| Failure mode | FM-02 (ignore_denied): agent bỏ qua kết quả approval bị từ chối |
| Đối chứng | Cùng claim@seed trên `fixed`: event #4 là `decision: {"action": "deny"}` — agent đọc đúng trạng thái denied và từ chối hoàn tiền |
| Regression test | `test_lab9_approval_bypass` trong `tests/test_lab9_graders.py` — `ApprovalBypass.evaluate` trả True khi `refund_count>0` và `approval_ok=False`; đã thấy FAIL trên `seeded_regression` và PASS trên `fixed` |
| Chưa chắc chắn | Trace không cho biết tại sao bug xảy ra: có thể agent đọc sai field approval hoặc có logic rẽ nhánh sai; cần thêm logging ở bước xử lý approval result |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
