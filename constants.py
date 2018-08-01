class Command:
    help = "/help"
    start = "/start"
    menu = "/menu"


class ButtonAction:
    default = 0


class Patterns:
    phone_number_pattern = "(^09[0-9]{9}$)|(^9[0-9]{9}$)"
    pass


class MimeType:
    image = "image/jpeg"
    csv = "text/csv"
    xlsx = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class BotMessage:
    message_sent = "پیام شما ارسال شد"
    enter_message_to_send_message = "پیام خود را وارد کنید"
    enter_username_to_send_message = "نام کاربری شخص مورد نظر خود را ارسال کنید"
    choose_from_menu = "یکی از موارد زیر را انتخاب کنید"
    enter_received_code = "لطفا کد دریافتی خود را وارد کنید:"
    greeting = "سلام به بازوی *تلگرام* بله خوش آمدید\nلطفا شماره تلفن خود را وارد کنید:"


class ConversationData:
    username = "username"
    phone = "phone"
    client = "client"
    name = "name"
    pass


class ButtonMessage:
    sending_message = "ارسال پیام"
    show_me = "نمایش اطلاعات من"
    entering_webogram = "ورود به وبوگرام"
    yes = "بله"
    return_to_main_menu = "بازگشت به منوی اصلی"
    guide = "راهنما"


class SendingAttempt:
    first = 1


class Step:
    finish_and_register = "finish_and_register"
    wrong_location = "wrong_location"
    finish_and_relocate = "finish_and_relocate"
    finish_and_delete = "finish_and_delete"
    delete_location = "delete_location"
    ask_relocate = "ask_relocate"
    select_edit_or_delete = "select_edit_or_delete"
    ask_location = "ask_location"
    location_id_not_same_as_before = "location_id_not_same_as_before"
    location_id_inserted_already = "location_id_inserted_already"
    location_id_not_found = "location_id_not_found"
    wrong_location_id_fomat = "wrong_location_id_fomat"
    ask_location_id = "ask_location_id"
    show_guide = "show_guide"
    showing_menu = "showing_menu"
    conversation_starter = "conversation_starter"


class LogMessage:
    location_deleting = "location deleted successfully"
    location_updating = "successful updating of location"
    location_registering = "successful registering of location"
    successful_sending = "successful sending of message:"
    failed_sending = "failed sending of message:"
    successful_step_message_sending = "successful step message sending"
    failed_step_message_sending = "failure step message sending"


class UserData:
    latitude = "latitude"
    longitude = "longitude"
    location_id = "location_id"
    bot = "bot"
    send_message = "send_message"
    logger = "logger"
    session = "session"
    ask_picture = "ask_picture"
    message_type = "message_type"
    message_id = "message_id"
    sending_set_time = "sending_set_time"
    base_message = "base_message"
    db_msg = "db_msg"
    random_id = "random_id"
    sending_attempt = "sending_attempt"
    kwargs = "kwargs"
    user_id = "user_id"
    user_peer = "user_peer"
    step_name = "step_name"
    message = "message"
    attempt = "attempt"
    report_attempt = "report_attempt"
    doc_message = "doc_message"
    file_url = "file_url"
