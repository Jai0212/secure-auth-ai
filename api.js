const axios = require('axios');

const BACKEND_URL = 'https://secure-auth-ai.onrender.com/'

/**
 * Each function needs to be called using the axios package.
 * All functions are ASYNCHRONOUS
 * Data is stored in a PostgreSQL database
 * 
 * Example Usage:
 * import { initializePackageSAA, signUpSAA } from 'secure-auth-ai'
 * 
 * Each function returns a reponse object which has 3 attributes:
 * value (string) - will have any value that needs to be returned. If not, or in case of an error, this will be either an empty string or []
 * success (boolean) - will be true if request was successful, false otherwise
 * message (string) - will have a message for debugging in case of an error or a success message
 */


async function initializePackageSAA(otherDetails = null) {
    /**
     * Call this function first to initialize the package. It will return a unique token which refers to your table.
     * You will need this token to make further calls. Store it as a constant variable and use it as the first parameter in all other functions.
     * In case you need more tables, call this function multiple times, with each token referring to a different table.
     * 
     * By default, the table has the following columns: id, password, total_logins, prev_locations, prev_devices, prev_logins, attempts, all_attempts
     * DON'T alter these as they are used for authentication and security purposes.
     *
     * Example Usage:
     * const SECURE_AUTH_AI_TABLE_KEY = await initializePackageSAA(["email", "phone_number"]);
     * 
     * @param {string[]} [otherDetails] - Optional parameter to add additional details to the table, if email and phone_number are passed, it will add two columns: email and phone_number to the table. All new details will be stored as strings.
     * @returns {Object} The JSON response object.
     * @returns {string} returns.value - The generated table key or an empty string in case of an error.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const response = await axios.post(`${BACKEND_URL}/initialize-package`, {
            other_details: otherDetails
        });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function signUpSAA(SECURE_AUTH_AI_TABLE_KEY, password, otherDetails = null, uniqueIdentifiers = null) {
    /**
     * Used to sign up a new user. It will return a unique token which refers to the user MFA key. The user should be asked to store this key safely.
     * This will thus add a new row to your table.
     * The user password will be tokenized and stored in the table.
     * The location of the user will be accessed as well as the device information and stored in the table for security purposes.
     * 
     * All unique identifiers must also be present in other details.
     * 
     * Example Usage:
     * const response = await signUpSAA(SECURE_AUTH_AI_TABLE_KEY, "user_password", {"email": "placeholder_mail.com", "phone_number": "99999999"}, "email");
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @param {string} password - The user password.
     * @param {Object.<string, string>} [otherDetails] - Optional parameter to add additional details to the user, first value refers to the table column and the second refers to the actual value. Make sure these columns exist from before.
     * @param {string[]} [uniqueIdentifiers] - Optional parameter to add unique identifiers to the user, if email is passed, it will be used as the unique identifier for the user, so it will not allow the user to sign up if some other user has previously signed up with that email.
     * @returns {Object} The JSON response object.
     * @returns {string} returns.value - The generated MFA key or an empty string in case of an error.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const deviceInfo = LocationAndDevice.getDeviceInfo();
        const device = deviceInfo.userAgent;

        const { latitude, longitude } = await LocationAndDevice.getCoordinates();
        const location = [String(latitude), String(longitude)];

        const response = await axios.post(`${BACKEND_URL}/sign-up`, {
            SECURE_AUTH_AI_TABLE_KEY,
            password,
            location,
            device,
            other_details: otherDetails,
            unique_identifiers: uniqueIdentifiers
        });

        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function logInSAA(SECURE_AUTH_AI_TABLE_KEY, password, otherDetails) {
    /**
     * Used to login a user.
     * The location of the user will be accessed as well as the device information and stored in the table for security purposes.
     * 
     * Example Usage:
     * const response = await logInSAA(SECURE_AUTH_AI_TABLE_KEY, "user_password", {"email": "placeholder_mail.com", "phone_number": "99999999"});
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @param {string} password - The user password.
     * @param {Object.<string, string>} otherDetails - Details to identify the user, first value refers to the table column and the second refers to the actual value.
     * @returns {Object} The JSON response object.
     * @returns {string} returns.value - Empty string in case of error or success, otherwise returns "MFA", to indicate user needs to use MFA
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const deviceInfo = LocationAndDevice.getDeviceInfo();
        const device = deviceInfo.userAgent;

        const { latitude, longitude } = await LocationAndDevice.getCoordinates();
        const location = [String(latitude), String(longitude)];

        const response = await axios.post(`${BACKEND_URL}/log-in`, {
            SECURE_AUTH_AI_TABLE_KEY,
            password,
            location,
            device,
            other_details: otherDetails
        });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function getUserDetailsSAA(SECURE_AUTH_AI_TABLE_KEY, identifier, value) {
    /**
     * Used to get user details
     * 
     * Example Usage:
     * const response = await getUserDetailsSAA(SECURE_AUTH_AI_TABLE_KEY, "email", "placeholder_mail.com");
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @param {string} identifier - The unique identifier to identify the user, it should be a column name.
     * @param {string} value - The value to identify the user.
     * @returns {Object} The JSON response object.
     * @returns {any[]} returns.value - The details of the user or an empty list in case of an error.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const response = await axios.post(`${BACKEND_URL}/get-user-details`, {
            SECURE_AUTH_AI_TABLE_KEY,
            identifier, value
        });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function getAllDetailsSAA(SECURE_AUTH_AI_TABLE_KEY) {
    /**
     * Used to get all table data.
     * 
     * Example Usage:
     * const response = await getAllDetailsSAA(SECURE_AUTH_AI_TABLE_KEY);
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @returns {Object} The JSON response object.
     * @returns {any[]} returns.value - The table data or an empty list in case of an error.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const response = await axios.post(`${BACKEND_URL}/get-all-details`, { SECURE_AUTH_AI_TABLE_KEY });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function updateUserDetailsSAA(SECURE_AUTH_AI_TABLE_KEY, identifier, value, details, breakDefaults = false) {
    /**
     * Used to update user details.
     * 
     * Example Usage:
     * const response = await updateUserDetailsSAA(SECURE_AUTH_AI_TABLE_KEY, "email", "placeholder_mail.com", {"email": "new_mail.com"});
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @param {string} identifier - The unique identifier to identify the user, it should be a column name.
     * @param {string} value - The value to identify the user.
     * @param {Object.<string, string>} details - Details to update, first value refers to the table column and the second refers to the actual value.
     * @param {boolean} [breakDefaults=false] - Optional parameter to update the default columns, set it to true if you want to update the default columns. This NOT recommended as it can lead to the backend and security measuers not working properly.
     * @returns {Object} The JSON response object.
     * @returns {string} returns.value - Empty string.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const response = await axios.post(`${BACKEND_URL}/update-user-details`, {
            SECURE_AUTH_AI_TABLE_KEY,
            identifier,
            value,
            details,
            break_defaults: breakDefaults
        });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function addColumnSAA(SECURE_AUTH_AI_TABLE_KEY, columnName) {
    /**
     * Used to add a new column to the table. The the data will be stored as a string.
     * 
     * Example Usage:
     * const response = await addColumnSAA(SECURE_AUTH_AI_TABLE_KEY, "age");
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @param {string} columnName - The name of the new column to be added.
     * @returns {Object} The JSON response object.
     * @returns {string} returns.value - Empty string.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const response = await axios.post(`${BACKEND_URL}/add-column`, {
            SECURE_AUTH_AI_TABLE_KEY,
            column_name: columnName
        });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function removeColumnSAA(SECURE_AUTH_AI_TABLE_KEY, columnName) {
    /**
     * Used to remove a column from the table.
     * 
     * Example Usage:
     * const response = await removeColumnSAA(SECURE_AUTH_AI_TABLE_KEY, "age");
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @param {string} columnName - The name of the column to be removed. This should not be one of the default columns as specified in the initializePackageSAA function.
     * @returns {Object} The JSON response object.
     * @returns {string} returns.value - Empty string.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const response = await axios.post(`${BACKEND_URL}/remove-column`, {
            SECURE_AUTH_AI_TABLE_KEY,
            column_name: columnName
        });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function removeUserSAA(SECURE_AUTH_AI_TABLE_KEY, identifier, value) {
    /**
     * Used to remove a user from the table. A row will be removed.
     * 
     * Example Usage:
     * const response = await removeUserSAA(SECURE_AUTH_AI_TABLE_KEY, "email", "placeholder_mail.com");
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @param {string} identifier - The unique identifier to identify the user, it should be a column name.
     * @param {string} value - The value to identify the user.
     * @returns {Object} The JSON response object.
     * @returns {string} returns.value - Empty string.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const response = await axios.post(`${BACKEND_URL}/remove-user`, {
            SECURE_AUTH_AI_TABLE_KEY,
            identifier, value
        });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

async function verifyMfaSAA(SECURE_AUTH_AI_TABLE_KEY, providedMfaKey, identifier, value) {
    /**
     * Used to verify the MFA key of the user. This should be done when the function logInSAA return "MFA".
     * On successful verification, it returns a new MFA key for the user for future use. The user should be asked to store this key safely.
     * 
     * Example Usage:
     * const response = await verifyMfaSAA(SECURE_AUTH_AI_TABLE_KEY, "sample_mfa_key", "email", "placeholder_mail.com");
     * 
     * @param {string} SECURE_AUTH_AI_TABLE_KEY - The unique token referring to your table.
     * @param {string} providedMfaKey - The MFA key provided by the user.
     * @param {string} identifier - The unique identifier to identify the user, it should be a column name.
     * @param {string} value - The value to identify the user.
     * @returns {Object} The JSON response object.
     * @returns {string} returns.value - Empty string in case of error/failure or a new MFA key for the user in case of success.
     * @returns {boolean} returns.success - A boolean indicating the success status.
     * @returns {string} returns.message - A message for debugging in case of an error or a success message.
     */
    try {
        const response = await axios.post(`${BACKEND_URL}/verify-mfa`, {
            SECURE_AUTH_AI_TABLE_KEY,
            provided_mfa_key: providedMfaKey,
            identifier,
            value
        });
        return response.data;
    } catch (error) {
        return handleError(error);
    }
}

function handleError(error) {
    if (error.response) {
        return {
            value: "",
            success: false,
            message: `API ERROR: ${error.response.data.message}`
        };
    } else if (error.request) {
        return {
            value: "",
            success: false,
            message: 'API ERROR: No response received from the server.'
        };
    } else {
        return {
            value: "",
            success: false,
            message: `API ERROR: ${error.message}`
        };
    }
}

class LocationAndDevice {
    /**
     * The functions in this class are used to find out the coordinates and device info of the user for security purposes.
     */
    static async getCoordinates() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject('Geolocation is not supported by this browser.');
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    resolve({ latitude, longitude });
                },
                (error) => {
                    reject(`Error occurred while retrieving location: ${error.message}`);
                }
            );
        });
    }

    static getDeviceInfo() {
        const userAgent = navigator.userAgent;
        const platform = navigator.platform;
        const deviceInfo = {
            userAgent,
            platform,
        };
        return deviceInfo;
    }
}

module.exports = {
    initializePackageSAA,
    signUpSAA,
    logInSAA,
    getUserDetailsSAA,
    getAllDetailsSAA,
    updateUserDetailsSAA,
    addColumnSAA,
    removeColumnSAA,
    removeUserSAA,
    verifyMfaSAA,
};
