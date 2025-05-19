# CS 145 Project 2

## Author and collaborators
### Author name
Nguyễn Hồng Anh - 23021466<br>
Trần Ánh Duy - 23021506<br>
Đậu Đức Hiếu - 23021546<br>

## Report

### Thuật toán định tuyến Link-State (LSrouter)

Thuật toán định tuyến Link-State (LS) được triển khai trong dự án này cho phép mỗi router tính toán đường đi ngắn nhất đến tất cả các nút khác trong mạng bằng cách sử dụng thông tin topo toàn cục, thu được thông qua việc lan truyền các gói tin link-state (LSA).

Mỗi router duy trì các thành phần:
- Biến `links_info`: ánh xạ các hàng xóm trực tiếp với cổng và chi phí liên kết tương ứng.
- Cơ sở dữ liệu link-state (`lsdb`): lưu thông tin link-state mới nhất của tất cả router đã biết (bao gồm chính nó). Mỗi mục gồm số thứ tự (`sequence number`) và từ điển ánh xạ hàng xóm với chi phí tương ứng.
- Bảng định tuyến `forwarding_table`: ánh xạ địa chỉ đích đến cổng cần gửi tiếp, dựa trên kết quả thuật toán Dijkstra từ dữ liệu `lsdb`.

Khi có liên kết được thêm hoặc xóa:
1. Router cập nhật lại `links_info`.
2. Tăng `sequence number` (`seq_num`).
3. Cập nhật lại thông tin của chính nó trong `lsdb`.
4. Chạy lại thuật toán Dijkstra để cập nhật bảng định tuyến `forwarding_table`.
5. Gửi link-state mới tới tất cả các hàng xóm.

Ngoài ra, router cũng định kỳ gửi lại link-state của mình kể cả khi không có thay đổi, nhằm đảm bảo tính ổn định và khả năng phục hồi khi có thay đổi không được phát hiện.

Khi nhận được gói LSA từ router khác, router sẽ kiểm tra `sequence number`:
- Nếu gói tin mới hơn (sequence cao hơn), thì cập nhật `lsdb`, tính lại bảng định tuyến và phát tán gói tin đó cho các hàng xóm khác (trừ người gửi).

Cơ chế này đảm bảo rằng tất cả các router cuối cùng sẽ hội tụ về cùng một cái nhìn nhất quán về mạng, từ đó tính được đường đi ngắn nhất đúng ngay cả khi topology thay đổi.
