## Requirements	
Download shape_predictor_68_face_landmarks predictor https://drive.google.com/drive/folders/1wPihpGo8uJPC1Xk1HBYU4jmG1_OKXofN?usp=drive_link

Install the required Python libraries by running: pip install PyQt5 opencv-python dlib numpy Pillow.

## Demo

- **Initialization**: Run `Main.py` to initiate the application.

## Registration of a New User
- **Initiating Registration**: Click the **Register User** button to begin the registration process. Ensure your face is aligned within the camera's view as directed by on-screen prompts.
- **Capturing and Entering User Details**: The system will capture your iris and prompt you to input your details (ID, Name, Age, and Blink count). After filling in the details, click **OK** to complete registration.
- **Password Protection**: A text box will appear for you to enter passwords that you wish to secure.

## Verification of a Registered User
- **Initiating Verification**: Select the **Verify User** button to start the verification process. Ensure your face is positioned for the webcam to capture your iris.
- **Identification and Verification**: You will be asked to enter the identification number for the user identity you want to verify. The system compares your iris with the registered entries under the provided ID. Verification is successful if there's a match and the blink pattern is correct.

## Viewing Registered Users
- Click on the **Show Registered Users** button to access a list of all registered users.


