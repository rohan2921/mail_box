from mail_box.driver import apply_rules, download_mails_and_store, perform_actions

download_mails_and_store(
    "/home/rohan/Downloads/client_secret_813044147814-kjiu5odm4r9a31rc8k3vjk6b2q2kaudn.apps.googleusercontent.com.json"
)

meassages = apply_rules(
    "/home/rohan/.config/JetBrains/PyCharm2023.3/scratches/scratch_13.json"
)

perform_actions(
    "/home/rohan/Downloads/client_secret_813044147814-kjiu5odm4r9a31rc8k3vjk6b2q2kaudn.apps.googleusercontent.com.json",
    meassages,
    ["move to folder", "mark as read"],
)
