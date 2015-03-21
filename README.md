# ReadMe

#### Initialize The Environment Of Server

- sudo apt-get install imagemagick
- sudo apt-get install python (you must choose pyhton 2.7)
- sudo easy_install reportlab

#### How To Run It
you have to choices to run it.
first, run it on foreground.
```shell
    sudo python Main.py
```

second, run it on background
```shell
    sudo python Main.py start
```
by the way, you can run it by multily times.

third, stop all of the process by run following shell
```shell
    sudo python Main.py stop
```

### How To Use It

+ **Config File**
    * **example of config**

    ```json
    {
      "AccessId": "vdF8mZT6VSJaszCF",
      "AccessKey": "zGRHc1xfn46UN6Puy4DUhQyp83Sd86",
      "OSSFrom": {
        "ServerName": "oss-cn-hangzhou.aliyuncs.com",
        "QueueName": "frint-files-test"
      },
      "OSSTo": {
        "ServerName": "oss-cn-hangzhou.aliyuncs.com",
        "QueueName": "frint-thumbnails",
        "ExpireTime": ""
      },
      "MQS": {
        "ServerName": "http://eq6io89s97.mqs-cn-hangzhou.aliyuncs.com",
        "QueueName": "fpt-tbl"
      },
      "LogFile": "tmp/mylog.log",
      "PidPath": "tmp/pid/",
      "tbl_length": 3,
      "Tmp_Path": "tmp/",
      "Pdf_Path": {
        "source": "tmp/source",
        "transformed": "tmp/transformed",
        "toimg": "tmp/toimg",
        "wtmkfile": "resources/watermark.png"
      },
      "MySql": {
        "user": "root",
        "password": "password",
        "server_ip": "127.0.0.1"
      }
    }
    
    ```

    * **format of config**
    ```json
        ...
    ```



### DATA STRUCT
+ **Data Input**
 * **example of input**
```json
{
    "type":"convert_to_img",
    "key":"3ae331b867608c6eaa2bdf6ce2387dc0-3389f81a8634e620ea39032618c81a35832a8bef-pdf-63250",
    "id":"-124821",
    "handouts":"V11",
    "callback":"http://api.dev.fenyin.me/v2/manage/file/previewPrepared?key=3ae331b867608c6eaa2bdf6ce2387dc0-3389f81a8634e620ea39032618c81a35832a8bef-pdf-63250-pdf-tbl"
}
```
 * **format of input**
```json
{
    "type": "convert_to_img",
    "key": file_key,
    "id": file_id,
    "handouts": handouts,
    "callback": url
}
```
 `file_key` means the **file name on oss**, if the corresponding file is not exist on oss bucket or the file type is not pdf, then we will stop the following processes and delete the task;
`file_id` means the **id of file in mysql** or mongodb;
`handouts` means the **handout of file**;
`url` means the url we have to call to **tell server** we finish the task;

+ **Data Output**
 * **example of output**

    + upload the pdf file that was added watermark from origin pdf file to oss called `OSSTo`. the name of file on oss is **`file_key` + '-tbl'**
    + upload image from the first page of pdf file to oss called `OSSTo`. the name of file on oss is **`file_key` + '-img0'**
    + tell the server we finish the task





### DETAIL ####

about pyPdf:
http://pybrary.net/pyPdf/

