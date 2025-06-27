


/**
 * Fetch data from the soil sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllSoilSensors = async () => {
    const response = await fetch("https://api.lx-gateway.tech/api/soil");
    return response.json();
};

/**
 * Fetch data from the atmospheric sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllAtmosphericSensors = async () => {
    const response = await fetch("https://api.lx-gateway.tech/api/atmosphere");
    return response.json();
};

/**
 * Fetch data from the water sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllWaterSensors = async () => {
    const response = await fetch("https://api.lx-gateway.tech/api/water");
    return response.json();
};

/**
 * Fetch data from the plant sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllPlantSensors = async () =>
    (await fetch("https://api.lx-gateway.tech/api/plant")).json();


/**
 * Fetch data from the Threat sensor endpoint
 * @returns {Promise<Object>}
 */
export const fetchAllThreatSensors = async () => (await fetch("https://api.lx-gateway.tech/api/threat")).json();

export const fetchSensorAverages = async () => {
    const response = await fetch("https://api.lx-gateway.tech/api/averages");
    if (!response.ok) {
        throw new Error("Failed to fetch sensor averages");
    }
    return response.json();
};
