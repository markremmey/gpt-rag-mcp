from typing import Annotated
from datetime import datetime
from semantic_kernel.functions import kernel_function

@kernel_function(
        name="get_today_date",
        description="Retrieve today's date.",
    )
def get_today_date() -> Annotated[str, "The output is today's date in string format"]:
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    return f"Today's date is {today}"

@kernel_function(
        name="get_time",
        description="Retrieve the current time.",
    )
def get_time() -> Annotated[str, "The output is the current time (hour and minutes) in HH:MM format"]:
    # Get the current time (hour and minutes)
    current_time = datetime.now().strftime("%H:%M")
    return f"The current time is {current_time}"
