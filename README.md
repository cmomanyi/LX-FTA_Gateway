# LX-FTA_Gateway
This project simulates a secure smart agriculture network using four types of sensors that transmit data to a gateway (LX-FTA), which processes and securely sends this data to a simulated cloud API. The project emphasizes wireless transmission, encryption, authentication, and attack resilience.
 # testing different threats
1. Example: Spoofing Simulation Request (via curl or Postman)
   POST /api/validate
   Content-Type: application/json

        {
        "sensor_id": "sensor-001",
        "payload": "soil moisture: 42%",
        "ecc_signature": "fake_signature_zzz999"
        }
    This will trigger: <BR>

         {
         "status": "🔴 Spoofing Detected – ECC Signature Mismatch",
         "sensor": "sensor-001",
         "timestamp": "2025-05-18T14:42:30.000Z"
         } 
<br>

2. Sample Replay Attack Request 
   Legit Payload:
   POST /api/replay-protect
   
         {
         "sensor_id": "sensor-001",
         "payload": "temperature: 25C",
         "timestamp": "2025-05-18T14:58:00.000Z",
         "nonce": "abc-123-unique"
         }
    Replayed Payload (same nonce):
       POST /api/replay-protect
   
          {
          "sensor_id": "sensor-001",
          "payload": "temperature: 25C",
          "timestamp": "2025-05-18T14:58:05.000Z",
          "nonce": "abc-123-unique"
          }
          
   Response

         {
         "status": "🔴 Replay Detected – Duplicate Nonce",
         "sensor": "sensor-001",
         "timestamp": "2025-05-18T14:58:07.000Z",
         "nonce": "abc-123-unique"
         }


3. Simulate Slow Drift
   POST /api/drift-detect
   normal <br>

            {
               "sensor_id": "sensor-003",
               "values": [22.0, 22.1, 22.2, 22.3, 22.1, 22.0]
               }
   error <Br>

         {
         "sensor_id": "sensor-003",
         "values": [22.0, 22.5, 23.0, 23.5, 24.0, 24.5]
         }
   The second payload will likely trigger:

         {
         "status": "🔴 ML Evasion Attempt – Drift Behavior Detected",
         "sensor": "sensor-003",
         "timestamp": "...",
         "anomaly_scores": [...]
         }

Admin Console:
         {
            "policy_id": "restrict_ddos_threshold",
            "description": "Ensure DDoS threshold is not set too high for critical sensors.",
            "target_sensors": ["soil_1", "plant_2", "threat_4"],
            "rules": [
            {
            "type": "threshold_limit",
            "max_threshold": 10,
            "severity": "high",
            "action": "block"
            }
            ],
            "enforcement": "strict",
            "created_by": "admin",
            "version": "1.0"
            }

   