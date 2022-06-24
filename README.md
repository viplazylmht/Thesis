# Combination of template matching and deep learning in presciption recognition

## Thông tin khoá luận

- Tên đề tài tiếng Việt: Kết hợp so khớp mẫu và học sâu trong bài toán trích xuất thông tin đơn thuốc
- Tên đề tài tiếng Anh: Combination of template matching and deep learning in extracting presciption information

- GVHD: ThS. Lê Ngọc Thành và ThS. Trương Tấn Khoa
- GVPB: TS. Nguyễn Tiến Huy
- Nhóm sinh viên:
    - Nguyễn Hoàng Đức - MSSV: 18120018
    - Hà Văn Duy - MSSV: 18120339

- Bảo vệ vào ngày 12/07/2022 tại Hội đồng Khoa học máy tính 1, Trường Đại học Khoa học Tự nhiên, TP. HCM

## How to run

Phần xử lý thông tin đơn thuốc (server):

- Môi trường Linux: Di chuyển đến thư mục theo đường dẫn backend/PrescriptionRecognition, chạy lệnh `./auto_run.sh`

- Môi trường Windows: Sử dụng docker để khởi chạy server.

Phần ứng dụng:

- Mở thiết bị có cài đặt ứng dụng lên, truy cập vào ứng dụng và tiến hành chụp ảnh đơn thuốc để gửi về server trích xuất thông tin.

- Lưu ý: Thiết bị đầu cuối (máy tính chạy máy ảo hoặc thiết bị di động) phải nằm chung một mạng với máy chủ (backend server). Server phải mở kết nối để cho phép máy khách truy cập.

