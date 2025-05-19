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

### Thuật toán định tuyến Distance-Vector (DVrouter)

Thuật toán Distance-Vector (DV) hoạt động dựa trên nguyên lý lan truyền khoảng cách: mỗi router định kỳ gửi toàn bộ distance vector (tức là bảng ánh xạ từ đích đến chi phí) của mình cho tất cả các hàng xóm trực tiếp. Mỗi router không có cái nhìn toàn cục về mạng mà chỉ biết chi phí đến các đích qua từng neighbor.

Trong triển khai này, mỗi router duy trì các cấu trúc dữ liệu:
- `routing_table`: lưu distance vector hiện tại, ánh xạ từ đích đến tuple `(cost, port)`.
- `link_costs`: ánh xạ từ `port` đến `cost` – dùng để tính chi phí đến neighbor.
- `neighbor_dvs`: lưu distance vector của từng neighbor.
- `via`: ánh xạ từ đích đến router trung gian đầu tiên (neighbor đầu tiên) mà distance vector đi qua.

Khi router nhận được distance vector từ một neighbor, nó sử dụng thuật toán Bellman-Ford cục bộ: thử từng neighbor, cộng chi phí đến neighbor với chi phí từ neighbor đến đích, và chọn tuyến đường tốt nhất (tốn ít chi phí nhất). Nếu bảng distance vector của router thay đổi, router sẽ phát lại DV mới đến tất cả neighbor.

Để tránh vấn đề **count-to-infinity**, triển khai này sử dụng **Poisoned Reverse**: nếu router học được route đến một đích thông qua neighbor A, thì khi gửi DV trở lại cho A, router sẽ thông báo chi phí đến đích đó là vô cùng (`INFINITY = 16`). Điều này giúp A không quay lại dùng chính route đó.

Khi có liên kết mới, router sẽ thêm neighbor vào bảng, cập nhật chi phí, và tính lại distance vector. Khi một liên kết bị gỡ, các route liên quan bị loại bỏ, sau đó router cập nhật và lan truyền thông tin mới.

Router cũng gửi DV định kỳ mỗi `heartbeat_time` ms, ngay cả khi không có thay đổi, để đảm bảo cập nhật mạng kịp thời và phục hồi sau lỗi.

Distance-Vector là một thuật toán đơn giản, không yêu cầu truyền toàn bộ topology mạng như Link-State. Tuy nhiên, nó đòi hỏi cơ chế chống vòng lặp và mất thời gian hội tụ lâu hơn – điều đã được khắc phục phần nào bằng Poisoned Reverse trong dự án này.

## Citations

## Grading notes (if any)

## Extra credit attempted (if any)