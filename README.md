# SecureAuthAI

[![npm version](https://img.shields.io/npm/v/secure-auth-ai.svg)](https://www.npmjs.com/package/secure-auth-ai)


SecureAuthAI offers web developers a comprehensive solution for implementing secure sign-in functionalities. This npm package integrates multi-factor authentication (MFA), real-time PostgreSQL database management, statistical anomaly detection using Z-score calculation, and a custom AI model. Designed to enhance login security, it automates user management tasks and ensures robust protection against unauthorized access.

SecureAuthAI is an npm package designed for web developers that provides secure sign-in functionality with MFA, PostgreSQL database integration, anomaly detection, and AI-based security measures, automating all management tasks.  
It integrates seamlessly with popular web frameworks like React, Vue, and Angular.

## Features
- **AI Model:** Custom AI model for detecting unsafe login attempts based on location, device, time, and number of attempts.
- **Anomaly Detection:** Statistical methods (Z-Score Calculation) to identify anomalies and prevent unauthorized access.
- **MFA Integration:** Multi-Factor Authentication using a secret key to enhance login security.
- **Realtime PostgreSQL Database:** Store user details securely with customizable functions provided out-of-the-box.
- **Hassle-Free Implementation:** Pre-made functions handle database interactions, eliminating the need for manual API calls.
- **Security:** Passwords are tokenized, and user-specific details are automatically managed to prevent security breaches.


## Framework Support
SecureAuthAI integrates seamlessly with popular web frameworks:  

<div style="display: flex; justify-content: center;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/120px-React-icon.svg.png" alt="React" style="margin: 0 10px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Vue.js_Logo_2.svg/120px-Vue.js_Logo_2.svg.png" alt="Vue.js" style="margin: 0 10px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Angular_full_color_logo.svg/120px-Angular_full_color_logo.svg.png" alt="Angular" style="margin: 0 10px;">
</div>

## Installation & Usage:

Install SecureAuthAI via npm:
```bash
npm i secure-auth-ai
```

Import the package in your project:  
`import * as SAA from 'secure-auth-ai';`

Or import specific functions:  
`import { initializePackageSAA, signUpSAA } from 'secure-auth-ai'`

All functions are asynchronous and should be used with axios for HTTP requests:  
`const response = await initializePackageSAA()`

Each response has three attributes to it:  
* value (string) - will have any value that needs to be returned. If not, or in case of an error, this will be either an empty string or []
* success (boolean) - will be true if request was successful, false otherwise
* message (string) - will have a message for debugging in case of an error or a success message

When you first use the package, you must call the function `initializePackageSAA()` which will give you a token which must be used to refer to your table in other functions. This token is the first parameter in all other functions.


## Available Functions

* initializePackageSAA
* signUpSAA
* logInSAA
* verifyMfaSAA
* getUserDetailsSAA
* getAllDetailsSAA
* updateUserDetailsSAA
* addColumnSAA
* removeColumnSAA
* removeUserSAA

For detailed usage of each function, refer to the 'api.js' file in the 'frontend' directory.


## Technical Aspects

* Backend: Python backend hosted on Render.
* Database: PostgreSQL hosted on Neon.
* Package: Written in JavaScript, published on npm
* AI Model:
    * Created using:
        * XGBoost Classifier
        * Random Forest Classifier
    * Training Data based on change in:
        * Location
        * Device
        * Time
        * Attempts
* Anomaly Detection: Z-Score Calculation for detecting unusual login patterns.
* Prediction: Based on the variation in location, device, time & attempts, along with the anomaly detection, it is decided whether a particular login attempt is safe or not
        

### Files
* `backend/` - Core logic and AI model implementation.
* `frontend/` - API calls and frontend integration.


## Acknowledgments
Special thanks to Render, Neon, and npm for their support in hosting and distributing this package.

I worked on this project alone and am actively working to improve this package.

### Contact
For suggestions, feedback, collaborations, or bug reports, please contact me via email: your-email@example.com.*

Author and Date  
by Jai Joshi  
Updated on 19th July, 2024