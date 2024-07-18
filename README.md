# SecureAuthAI

[![npm version](https://img.shields.io/npm/v/secure-auth-ai.svg)](https://www.npmjs.com/package/secure-auth-ai)


SecureAuthAI offers web developers a comprehensive solution for implementing secure sign-in functionalities.  

This npm package integrates multi-factor authentication (MFA), real-time PostgreSQL database management, statistical anomaly detection using Z-score calculation, and a custom AI model.  

Designed to enhance login security, it automates user management tasks and ensures robust protection against unauthorized access.  

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
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/120px-React-icon.svg.png" alt="React" height="60" width="60" style="margin: 0 10px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Vue.js_Logo_2.svg/120px-Vue.js_Logo_2.svg.png" alt="Vue.js" height="60" width="60" style="margin: 0 10px;">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Angular_full_color_logo.svg/120px-Angular_full_color_logo.svg.png" alt="Angular" height="70" width="70" style="margin: -5 10px;">
</div>

## Installation & Usage:

Install SecureAuthAI via npm:
```bash
npm i secure-auth-ai
```

Import the package in your project:  
```bash
import * as SAA from 'secure-auth-ai';
```

Or import specific functions:  
```bash
import { initializePackageSAA, signUpSAA } from 'secure-auth-ai';
```

All functions are asynchronous and should be used with axios for HTTP requests:  
```bash
const response = await initializePackageSAA()
```

Each response has three attributes to it:  
- **value** - any value that needs to be returned. If not, or in case of an error, this will be either an empty string or []
- **success** - true if request was successful, false otherwise
- **message** - message for debugging in case of an error or a success message

When you first use the package, you must call the function `initializePackageSAA()` which will give you a token which must be used to refer to your table in other functions. This token is the first parameter in all other functions.


## Example JS
```bash
import { initializePackageSAA, signUpSAA, updateUserDetailsSAA, getUserDetailsSAA } from 'secure-auth-ai';
 
const SECURE_AUTH_AI_TABLE_KEY = await initializePackageSAA(["email"]);

const signUpResponse = await signUpSAA(SECURE_AUTH_AI_TABLE_KEY, "hello", {"email": "placeholder@example.com", "phone_number": "+123456789"});

if (signUpResponse.success) {
    const updateResponse = await updateUserDetailsSAA(SECURE_AUTH_AI_TABLE_KEY, "email", "placeholder@example.com", {"phone_number": "+199999999"});

    console.log(updateResponse.message)

    const detailsResponse = await getUserDetailsSAA(SECURE_AUTH_AI_TABLE_KEY, "email", "placeholder@example.com");

    console.log(detailsResponse.value)
}
```

## Example React
```bash
import React, { useEffect, useState } from 'react';
import { initializePackageSAA } from 'secure-auth-ai'; // Import the package

function App() {
  const [token, setToken] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchToken = async () => {
      try {
        const result = await initializePackageSAA(); // Call the function to generate a unique token
        setToken(result.value); // Store the unique token
      } catch (err) {
        setError('Error generating token');
      }
    };

    fetchToken();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>SecureAuthAI Package Demo</h1>
        {token ? (
          <p>Your unique token: {token}</p> // Display the unique token
        ) : (
          <p>{error || 'Generating token...'}</p>
        )}
      </header>
    </div>
  );
}

export default App;
```


## Example Vue.js
```bash
<template>
  <div>
    <h1>Welcome</h1>
    <p v-if="data.success">Key: {{ data.value }}</p>
    <p v-else>{{ error }}</p>
  </div>
</template>

<script>
import { initializePackageSAA } from 'secure-auth-ai'; // Import the package

export default {
  data() {
    return {
      data: { message: '', success: false, value: '' },
      error: ''
    };
  },
  async created() {
    try {
      const result = await initializePackageSAA(); // Call the function
      this.data = result; // Store the result
    } catch (error) {
      console.error('Error initializing package:', error);
      this.error = 'Error retrieving data';
    }
  }
};
</script>
```

Everytime the function `logInSAA` is called, using the AI model and anomaly detection, it is checked whether the login attempt is safe or not. If it is not safe, you are required to call `verifyMfaSSA` to do the MFA.

**NOTE**: Initally it can take about a minute to get a response as the backend needs to load up.

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

**NOTE**: All functions are asynchronous

For detailed usage of each function, refer to the `api.js` file in the `frontend` directory.


## Technical Aspects

* **Backend**: Python backend hosted on Render.
* **Database**: PostgreSQL hosted on Neon.
* **Package**: Written in JavaScript, published on npm
* **AI Model**:
    * Created using:
        * XGBoost Classifier
        * Random Forest Classifier
    * Training Data based on change in:
        * Location
        * Device
        * Time
        * Attempts
* **Anomaly Detection**: Z-Score Calculation for detecting unusual login patterns.
* **Prediction**: Based on the variation in location, device, time & attempts, along with the anomaly detection, it is decided whether a particular login attempt is safe or not
        

### Files
* `backend/` - Core logic and AI model implementation.
* `frontend/` - API calls and frontend integration.


## Webpack Configuration

If you're using React (Webpack) and encounter issues with missing core Node.js modules (like `crypto`), you may need to update your Webpack configuration. Add the following to your `webpack.config.js` (found inside `node_modules/react-scripts/config/`):

```js
resolve: {
  fallback: {
    crypto: false,
    // Add other fallbacks if necessary
  }
}
```

## Acknowledgments
Special thanks to Render, Neon, and npm for their support in hosting and distributing this package.

### Contact
*For suggestions, feedback, collaborations, or bug reports, please contact me via email: jj.joshijai@gmail.com*

Author and Date  
by Jai Joshi  
Updated on 19th July, 2024