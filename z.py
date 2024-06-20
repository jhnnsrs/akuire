import asyncio

import numpy as np
import sounddevice as sd

# Set the threshold for detecting a scream
THRESHOLD = 0.5


# Async function that simulates a long-running task
async def long_running_task():
    try:
        while True:
            print("Task is running...")
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print("Task has been cancelled")


# Function to check if the input audio exceeds the threshold


# Main function to set up the microphone stream and start the async task
async def main():
    task = asyncio.create_task(long_running_task())

    def detect_scream(indata, frames, time, status):
        volume_norm = np.linalg.norm(indata) * 10
        if volume_norm > THRESHOLD:
            print("Scream detected!")
            if not task.done():
                task.cancel()

    # Open the microphone stream
    with sd.InputStream(callback=detect_scream):
        print("Listening for screams...")
        await task


# Run the main function
asyncio.run(main())
