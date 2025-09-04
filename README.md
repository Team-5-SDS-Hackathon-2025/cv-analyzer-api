# CV Analyzer API
Xây dựng một ứng dụng web **MVP** cho phép người dùng **tải lên CV**, để hệ thống **tự động đánh giá** và **đề xuất câu hỏi phỏng vấn**.


## Công nghệ
- **Frontend**: React, UI Library (e.g., MUI, Ant Design, Tailwind CSS)
- **Backend**: Python (FastAPI), Unstructured, LangChain
- **Unstructured**:  
  - Sử dụng các mô hình AI phân tích tài liệu tích hợp sẵn (như **YOLO**) để **phân đoạn các phần trong tài liệu**, giúp **trích xuất văn bản có cấu trúc** từ các file phức tạp như **PDF, DOCX**.
- **LangChain**:  
  - Framework để xây dựng các ứng dụng AI như chatbot, hệ thống **RAG (Retrieval-Augmented Generation)**, và các **AI agent** bằng code đơn giản.
- **AI Model**: Gemini 2.5 Flash


## Workflow
**LangChain** sẽ đóng gói nội dung CV và gửi cho **Gemini** cùng một **prompt** cụ thể.  
**Gemini** phân tích và trả về kết quả có cấu trúc (**JSON**) bao gồm:
- Đánh giá CV  
- Danh sách câu hỏi phỏng vấn đề xuất



## Core Flow

### 1. **Tải lên (Upload)**
- Người dùng truy cập trang web và **tải file CV** (PDF, DOCX) lên hệ thống.

### 2. **Xử lý (Process)**
- Backend nhận file, **trích xuất nội dung** với **Unstructured**.  
- Sau đó **LangChain** gửi dữ liệu cùng prompt đến **Gemini** để phân tích.

### 3. **Hiển thị (Display)**
- Frontend nhận **kết quả JSON** từ backend.  
- Hiển thị đồng thời:
  - **Phần đánh giá CV**  
  - **Danh sách câu hỏi phỏng vấn được đề xuất**

