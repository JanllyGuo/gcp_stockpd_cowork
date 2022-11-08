# TibaMe AI-11102 stockpd co-work in GCP

## 檔案資料夾 [前置詞] 定義說明

00_**gcf**：代表程式碼是在 GCP Cloud Functions 開發並且運行

00_**deploy**：代表程式碼是在 GCP Cloud Run 開發並且運行

00_**vm**：代表程式碼是在 GCP Compute Engine 虛擬機器上開發並且運行

## 各個檔案資料夾的使用說明
### 01_gcf_get_stock_data_upload_storage
- 直接複製貼上 requirements.txt 的內容
- main.py
  ```python
  # f'stock-data      可替換成自己的 bucket 內所建立的資料夾名稱
  # Your bucket name  須替換成自己建立的 Cloud Storage bucket
  upload_storage(csvfile, f'stock-data/{stockid}.csv', 'Your bucket name')
  ```

### 02_deploy_get_stock_data_upload_storage
- 先進到該資料夾路徑後，再執行
  ```
  pip3 install -r requirements.txt
  ```
- main.py
  ```python
  # f'stock_data  可替換成自己的 bucket 內所建立的資料夾名稱
  # your bucket name  須替換成自己建立的 Cloud Storage bucket
  data.to_csv(f'stock_data/{stockid}.csv')

  upload_storage(f'stock_data/{stockid}.csv', f'stock-data/{stockid}_{today}.csv', 'your bucket name')
  ```
- Deploy a Python service to Cloud Run
  ```Shell Script
  gcloud config set project YOUR-PROJECT-ID
  
  gcloud run deploy --source .
  Source code location:               輸入程式碼目前的資料夾路徑
  Service name:                       輸入服務名稱(在 Cloud Run 管理介面中顯示的服務名稱)
  region:                             輸入區域代碼，如 32 us-west1 即輸入32
  Allow unauthenticated invocations:  輸入 y
  
  ** 註：上述執行方式並不會在 Container Registry 產生映像檔，但卻會在 Cloud Storage 產生一個 bucket **
  ```

### 03_gcf_get_stock_data_image_upload_storage
- 直接複製貼上 requirements.txt 的內容
- main.py
  ```python
  # f'stock-data 和 f'stock-image  可替換成自己的 bucket 內所建立的資料夾名稱
  # your bucket namee              須替換成自己建立的 Cloud Storage bucket
  # /tmp 是透過 Cloud Functions 使用「tmpfs」磁碟區的本機磁碟掛接點，寫入這個磁碟區的資料會儲存在記憶體中。不會產生費用，但會耗用記憶體資源
  upload_storage_doc(csvfile, f'stock-data/{stockid}.csv', 'your bucket name')
  
  file_path = '/tmp/' + f'{stockid}.png'  
  
  upload_storage_img(file_path, f'stock-image/{stockid}.png', 'your bucket name')
  ```

### 04_vm_get_stock_data_image_upload_storage
- 先進到該資料夾路徑後，再執行
  ```
  pip3 install -r requirements.txt
  pip3 install python-crontab
  ```
- upload_data_image.py
  ```python
  # stockpd-data 和 stockpd-image  須替換成自己建立的 Cloud Storage bucket
  # f'original                     可替換成自己的 bucket 內所建立的資料夾名稱
  upload_storage_file(csvfile, f'{stockid}.csv', 'stockpd-data')
  
  upload_storage_img(f'{stockid}.png', f'original/{stockid}.png', 'stockpd-image')
  ```
- run_upload_data_image.py
  ```python
  # 這支py 是使用 python-crontab 來進行排程，通常寫好後就不太會更動!
  
  my_cron = CronTab(user='stockpd') # 建立這個排程的使用者
  job = my_cron.new(command='/usr/bin/python3 /home/stockpd/get-stock-data-image-upload-storage/upload_data_image.py', comment='uploadStorage')
  job.setall('30 14 * * *') # 設定每天下午 14:30 執行 upload_data_image.py
  ```
- 若需要調整排程設定 (可參考 cat_crontab_uploadStorage.txt 內容，該檔案是將目前虛擬機器上的排程設定內容進行匯出)
  ```Shell Script
  crontab -l    # 檢視目前該帳號所建立的排程內容
  crontab -e    # 編輯目前該帳號所建立的排程內容
  ```

### 05_deploy_get_stock_data_image_upload_storage
- 先進到該資料夾路徑後，再執行
  ```
  pip3 install -r requirements.txt
  ```
- main.py
  ```python
  # stockpd-data 和 stockpd-image  須替換成自己建立的 Cloud Storage bucket
  # f'original                     可替換成自己的 bucket 內所建立的資料夾名稱
  utils.upload_storage_file(csvfile, f'{stockid}.csv', 'stockpd-data')
  
  utils.upload_storage_img(f'{stockid}.png', f'original/{stockid}.png', 'stockpd-image')
  ```
- 構建程式碼
  ```Shell Script
  gcloud config set project YOUR-PROJECT-ID
  gcloud builds submit  --tag gcr.io/$GOOGLE_CLOUD_PROJECT/xxx-xxx-dev:0.0.1
  ```
- 進行部署
  **到 Cloud Run 建立服務**
 
### 06_vm_prediction_yolov7_singlefile_test
- 先把 **best.pt 和 traced_model.pt** 這兩個檔案複製到該程式碼資料夾路徑
  - 因為這兩個檔案無法上傳到 github，所以沒有跟程式碼放一起，應該會開雲端硬碟共用(這部份**待補**...)
- 先進到該資料夾路徑後，再執行
  ```
  pip3 install -r requirements.txt
  ```
- download_images.py
  ```python
  # 替換成自己的 bucket 和 資料夾名稱
  sourcefile = 'stock-image/2303_2000-06-08.png'
  bucketname = 'your bucket_name'
  ```
- upload_images.py
  ```python
  # 替換成自己的 bucket 和 資料夾名稱
  bucketname = 'your bucket_name'
  dstfile = 'stock-image/2303_2000-06-08_yolov7.png'
  ```
- execute.sh
  ```Shell Script
  # $account                用自己的帳號替換掉
  # prediction-test-yolov7  程式碼的資料夾名稱(如不一樣，請自行替換)
  cd /home/$account/prediction-test-yolov7/
  ```
- 變更 execute.sh 權限
  ```Shell Script
  chmod +x execute.sh
  ```
- 設定 linux crontab 排程
  ```Shell Script
  crontab -e        # 用自己的帳號建立排程
  sudo crontab -e   # 如果自己的帳號權限不足，則使用 root 來建立
  
  # 排程器的內容 (記得替換 帳號stockpd 和 程式碼資料夾路徑prediction-test-yolov7 )
  40 14 * * * /bin/sh /home/stockpd/prediction-test-yolov7/execute.sh  # runShell
  ```
  
### 07_vm_prediction_yolov7_stocklist_test

- **做法大致上如 06_vm_prediction_yolov7_singlefile_test**

### 08_deploy_prediction_prophet_test
- 先進到該資料夾路徑後，再執行
  ```
  pip3 install -r requirements.txt
  ```
- app.py
  ```python
  # 替換成自己的 bucket 和 資料夾名稱
  download_bucket = 'stockpd-data'
  upload_bucket = 'stockpd-image'
  
  download_storage(f'{stockid}.csv', f'stockData/{stockid}.csv', download_bucket)
  upload_storage(f'stockPred/{stockid}.png', f'prediction/{stockid}_prophet.png', upload_bucket)
  ```
- 構建程式碼
  ```Shell Script
  gcloud config set project YOUR-PROJECT-ID
  gcloud builds submit  --tag gcr.io/$GOOGLE_CLOUD_PROJECT/xxx-ooo-dev:0.0.1
  ```
- 進行部署
  **到 Cloud Run 建立服務**
  
### 09_vm_stockpd_linebot (待更新..)
- 先進到該資料夾路徑後，再執行
  ```
  pip3 install -r requirements.txt
  ```
- app01.py
  ```python
  # 替換 channel_access_token 和 channel_secret
  line_bot_api = LineBotApi("你自己的LINE channel_access_token")
  handler = WebhookHandler("你自己的LINE channel_secret")
  
  # 替換自己的 bucket 和 bucket 內的資料夾
  ```
  
### 10_deploy_stockpd_linebot
- 先進到該資料夾路徑後，再執行
  ```
  pip3 install -r requirements.txt
  ```
- app.py
  ```python
  # 替換自己的 bucket 和 bucket 內的資料夾
  ```
- 使用 ngrok 本地測試 (記得要先註冊 ngrok)
  ```Shell Script
  # 下載 ngrok
  wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
  # 解壓縮
  unzip ngrok-stable-linux-amd64.zip
  # 變更權限
  sudo chmod u+x ngrok
  # 使用自己的 ngrok token進行授權
  ./ngrok authtoken YOUR-NGROK-TOKEN
  # 運行 ngrok
  ./ngrok http --region ap 8080
  ```
  - **本地端使用 ngrok測試成功後，再做 Cloud Build -> Cloud Run (因為 ngrok 每次只能運行兩小時)**
- 構建程式碼
  ```Shell Script
  gcloud config set project YOUR-PROJECT-ID
  gcloud builds submit  --tag gcr.io/$GOOGLE_CLOUD_PROJECT/stockpd_linebot-dev:0.0.1
  ```
- 進行部署

  **到 Cloud Run 建立服務，並指定環境變數**
  ```
  LINE_CHANNEL_ACCESS_TOKEN: 自己的 LINE channel_access_token
  LINE_CHANNEL_SECRET: 自己的 LINE channel_secret
  ```
- LINE Messaging API
  - **將 Cloud Run 佈署成功後產出的網址連結，貼到 Webhook**
    - 例如 https://run-stockpd-linebot-test-wwwkdfb5ja-oo.a.run.app `/callback`

### 11_vm_prediction_yolov4_test (待上架..)
- 預計 11/9 - 11/11
- 

## 下載所有程式碼(在 GCP Cloud Shell 開啟)

https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/JanllyGuo/gcp_stockpd_cowork&cloudshell_open_in_editor=README.md&cloudshell_workspace=.

**注意：在 Cloud Shell 編寫程式碼時，一定要先指定專案ID (gcloud config set project YOUR-PROJECT-ID)**
