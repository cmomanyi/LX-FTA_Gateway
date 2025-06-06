


/**
 * Fetch data from the soil sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllSoilSensors = async () => {
    const response = await fetch("http://localhost:8000/api/soil");
    return response.json();
};

/**
 * Fetch data from the atmospheric sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllAtmosphericSensors = async () => {
    const response = await fetch("http://localhost:8000/api/atmosphere");
    return response.json();
};

/**
 * Fetch data from the water sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllWaterSensors = async () => {
    const response = await fetch("http://localhost:8000/api/water");
    return response.json();
};

/**
 * Fetch data from the plant sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllPlantSensors = async () =>
    (await fetch("http://127.0.0.1:8000/api/plant")).json();


/**
 * Fetch data from the Threat sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllThreatSensors = async () => (await fetch("http://127.0.0.1:8000/api/threat")).json();