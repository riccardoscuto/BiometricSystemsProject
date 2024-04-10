## Requirements	
Download shape_predictor_68_face_landmarks predictor https://drive.google.com/drive/folders/1wPihpGo8uJPC1Xk1HBYU4jmG1_OKXofN?usp=drive_link

Install the required Python libraries by running: pip install PyQt5 opencv-python dlib numpy Pillow.

## Demo
Start the Application: run Main.py

**Register a New User**:
Click on the "Register User" button to start the registration process.
Position your face within the camera's field of view as indicated by the on-screen instructions.
The system will  capture your  and prompt you to enter user details (ID, Name, Age, Blink count).
After entering the details, click "OK" to complete the registration. 
A text box will open where you can enter passwords to be protected.

**Verify Registered User**:
Select "Verify User" to start verification.
Position your face for the webcam.
After iris capture, you will be prompted to enter the identification number of the user identity you wish to verify against.
The system compares your iris with registered entries based on the provided ID.
A match and correct blink pattern confirm successful verification.

Click on the "Show Registered Users" button to display a list of all registered users.
