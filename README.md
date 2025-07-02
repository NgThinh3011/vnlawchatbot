# VNlawchatbot 🚦📘  
Hệ thống hỏi đáp về luật giao thông Việt Nam dựa trên mô hình RAG nâng cao (Advanced Retrieval-Augmented Generation).  
Dự án này được thiết kế nhằm hỗ trợ người dân dễ dàng tra cứu, hiểu và áp dụng các quy định pháp luật về giao thông, với khả năng truy xuất chính xác và trả lời mạch lạc theo ngữ cảnh.

---

## 📚 Bộ Dữ Liệu

Nguồn dữ liệu được thu thập trực tiếp từ trang **vbpl.vn** – Cổng thông tin chính thức của Chính phủ về văn bản quy phạm pháp luật.  
Quy trình xử lý dữ liệu gồm:

- **Thu thập**: Sử dụng trình thu thập dữ liệu để lấy văn bản luật liên quan đến lĩnh vực giao thông (luật, nghị định, thông tư).
- **Tiền xử lý**: Chuẩn hóa văn bản, loại bỏ nội dung trùng lặp, chuyển đổi định dạng HTML/PDF sang plain text.
- **Làm sạch & chuẩn hóa**: Bảo toàn cấu trúc điều/khoản để thuận tiện cho việc chunking và truy vấn.

---

## 🧠 Hệ Thống Advanced RAG

Hệ thống được mở rộng từ kiến trúc RAG truyền thống với các cải tiến sau:

### ⚙️ Mô hình hệ thống:

![Advanced RAG Architecture](./images/advanced_rag_pipeline.png) *(Thêm hình minh họa kiến trúc tại đây)*

### 🧩 Các module mới tích hợp:

- **Recursive Chunking Module**: Chia nhỏ văn bản theo cấu trúc pháp lý (chương, điều, khoản), giúp giữ ngữ nghĩa và đảm bảo độ đầy đủ thông tin.
- **Hybrid Search Engine**: Kết hợp **vector search (semantic)** và **keyword-based search (BM25)** để nâng cao độ chính xác truy xuất.
- **Legal-aware Embedding Model**: Sử dụng mô hình embedding được fine-tune để biểu diễn ngữ nghĩa văn bản luật.
- **Answer Synthesizer**: Tạo câu trả lời logic, chính xác và trích dẫn được nguồn từ văn bản gốc.

---

## 🔍 Quy Trình Triển Khai

1. **Chunking**:  
   - Áp dụng **recursive chunking** để chia văn bản pháp luật thành các đoạn có cấu trúc rõ ràng (Điều, Khoản).
   - Mỗi chunk được lưu trữ cùng metadata như số điều, tên luật, năm ban hành.

2. **Tìm kiếm truy xuất (Retrieval)**:  
   - Triển khai **Hybrid Search**:  
     - **BM25** để tìm kiếm dựa trên từ khóa.  
     - **FAISS + embedding semantic search** để tìm kiếm theo ngữ nghĩa.

3. **Sinh câu trả lời (Generation)**:  
   - Sử dụng mô hình RAG để kết hợp đoạn văn truy xuất và sinh câu trả lời.  
   - Áp dụng **chain-of-thought prompting** để mô hình lý luận từng bước trước khi đưa ra kết luận cuối cùng.

---

## 📊 Đánh Giá Hệ Thống

Các phương pháp truy xuất được so sánh:

| Phương pháp            | Hit@10 | MAP@10 | MRR@10 |
|------------------------|--------|--------|--------|
| BM25                   | 0.82   | 0.78   | 0.75   |
| FAISS + Legal Embedding| 0.91   | 0.88   | 0.86   |
| Hybrid (FAISS + BM25)  | **0.94** | **0.91** | **0.89** |

📈 *Hình minh họa biểu đồ so sánh:*  
![Evaluation Results](./images/evaluation_chart.png)

---

## 🖥️ Giao Diện Người Dùng

Hệ thống tích hợp một giao diện đơn giản, trực quan để:

- Nhập câu hỏi liên quan đến luật giao thông
- Hiển thị kết quả truy xuất (trích dẫn cụ thể theo điều/khoản)
- Trình bày câu trả lời được sinh từ mô hình
- Cho phép tra cứu văn bản gốc

![UI Demo](./images/ui_demo.png)

---

## 🚀 Khởi Chạy Dự Án

```bash
git clone https://github.com/yourusername/VNlawchatbot.git
cd VNlawchatbot
pip install -r requirements.txt
python run_app.py
