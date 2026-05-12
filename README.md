# Constraint based pattern data mining

Khai phá luật kết hợp định lượng có ràng buộc. Dự án so sánh quy trình FP-Growth baseline (lọc ràng buộc hậu xử lý) với phương pháp đề xuất (cắt tỉa trong quá trình khai phá) dựa trên ngưỡng `avg(price)`.

## Điểm nổi bật
- Quy trình notebook đầy đủ từ tiền xử lý đến đánh giá
- Baseline FP-Growth với lọc hậu xử lý ràng buộc
- In-mining pruning để giảm số mẫu ứng viên sớm
- Kết quả tái lập, xuất ra CSV/JSON/PKL/PNG

## Cấu trúc thư mục
- [data/](data/) Dữ liệu thô
- [notebooks/](notebooks/) Notebook cho toàn bộ thí nghiệm
- [outputs/](outputs/) Artifacts sinh ra
- [src/](src/) Cài đặt lõi và tiện ích
- [README.md](README.md) Tài liệu dự án

## Yêu cầu
- Python 3.9+ khuyến nghị
- Jupyter hoặc VS Code với Python extension
- Thư viện phụ thuộc được cài theo nhu cầu trong notebook qua `ensure_package`

## Khởi động nhanh
```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Mở notebook trong VS Code và chạy theo đúng thứ tự (xem mục bên dưới).

## Quy trình notebook
Chạy notebook theo thứ tự sau:
1. [notebooks/data_preprocessing.ipynb](notebooks/data_preprocessing.ipynb) Đọc và làm sạch dữ liệu, sinh transactions và item price artifacts
2. [notebooks/baseline_post-processing.ipynb](notebooks/baseline_post-processing.ipynb) Baseline FP-Growth + lọc ràng buộc hậu xử lý
3. [notebooks/proposed_in-mining_pruning.ipynb](notebooks/proposed_in-mining_pruning.ipynb) Phương pháp đề xuất (In-mining pruning)
4. [notebooks/evaluation.ipynb](notebooks/evaluation.ipynb) So sánh kết quả và xuất metrics

## Yêu cầu dữ liệu
Notebook tiền xử lý sẽ tìm dataset CSV/XLSX dưới thư mục gốc dự án (duyệt đệ quy, bỏ qua [outputs/](outputs/)). Dataset cần có các cột sau (phân biệt hoa thường):
- `BillNo`
- `Itemname`
- `Price`
Cột tùy chọn:
- `Quantity`

File mẫu có sẵn tại [data/Assignment-1_Data.csv](data/Assignment-1_Data.csv).

## Cấu hình
Notebook đọc cấu hình từ biến môi trường (tùy chọn):
- `PROJECT_ROOT` Ghi đè thư mục gốc dự án
- `OUTPUT_DIR` Thư mục lưu artifacts (mặc định: [outputs/](outputs/))
- `DATA_DIR` Thư mục dữ liệu (để kiểm tra nhanh)
- `MIN_SUPPORT_RATIOS` Danh sách tỷ lệ, ví dụ `0.05,0.04,0.03`
- `PRICE_THRESHOLD` Ngưỡng ràng buộc `avg(price)`
- `MARKET_BASKET_DATASET_PATH` Đường dẫn dataset cụ thể
- `TRANSACTION_ID_COLUMN`, `ITEM_COLUMN`, `PRICE_COLUMN`, `QUANTITY_COLUMN` Ánh xạ tên cột

## Đầu ra
Artifacts được lưu trong [outputs/](outputs/), bao gồm:
- Transactions và item price (pickle)
- Kết quả baseline và proposed
- Bảng metrics (CSV)
- Tóm tắt đánh giá (JSON)
- Biểu đồ so sánh runtime (PNG)

## Xử lý sự cố
- Không tìm thấy dataset: đặt file CSV/XLSX hợp lệ ở thư mục gốc hoặc cấu hình `MARKET_BASKET_DATASET_PATH`.
- Thiếu artifacts: chạy notebook theo đúng thứ tự để tạo đủ dữ liệu cho các bước sau.