flowchart TD
    A[用户交互] -->|触摸屏/GUI| B[Flask Web接口]
    A -->|语音指令| B
    B --> C[机器人底座控制]
    B --> D[OBS摄像头控制]
    C --> E[机器人移动]
    D --> F[摄像头拍照/录像]
    E --> G[到达书架位置]
    F --> H[采集图书图像]
    G --> H
    H --> I[存储图像/视频]
    I --> J[命名并保存]
    J --> K[完成盘点]
    
    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#f96,stroke:#333
    style D fill:#f96,stroke:#333
    style E fill:#9f9,stroke:#333
    style F fill:#9f9,stroke:#333
    style G fill:#9cf,stroke:#333
    style H fill:#9cf,stroke:#333
    style I fill:#9cf,stroke:#333
    style J fill:#9cf,stroke:#333
    style K fill:#f9f,stroke:#333
