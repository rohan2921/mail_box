from driver import apply_rules, download_mails_and_store

download_mails_and_store(
    "/home/rohan/Downloads/client_secret_813044147814-kjiu5odm4r9a31rc8k3vjk6b2q2kaudn.apps.googleusercontent.com.json"
)

meassages = apply_rules(
    "/home/rohan/.config/JetBrains/PyCharm2023.3/scratches/scratch_13.json"
)
