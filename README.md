# MHUTEMP Stack 02 Backend

Python/FastAPI backend implementation of the **MHUTEMP healthcare environmental monitoring architecture**.

Stack 02 was developed as an alternative implementation of the MHUTEMP Processing Layer to evaluate whether the same functional monitoring workflow can be preserved after replacing the original **Node.js/Express** backend with **Python/FastAPI**, while retaining **MongoDB** as the persistence technology.

---

## Architecture

The Stack 02 configuration is:

```text
ESP32 Monitoring Node
        |
        | WebSocket / HTTP
        v
Python / FastAPI Backend
        |
        v
MongoDB
        |
        v
Next.js Monitoring Interface
```

The architectural responsibilities evaluated in Stack 02 are:

| Layer | Technology |
|---|---|
| Acquisition | ESP32 |
| Communication | WebSocket / HTTP |
| Processing | Python / FastAPI |
| Persistence | MongoDB |
| Presentation | Next.js |

---

## Purpose

Stack 02 is part of the experimental evaluation of the **MHUTEMP reference software architecture**.

The main objective of this implementation is to evaluate a selected **Processing Layer technology substitution**:

```text
Stack 01
Node.js / Express + MongoDB

              |
              | Processing technology substitution
              v

Stack 02
Python / FastAPI + MongoDB
```

The same monitoring responsibilities and message flow are preserved while changing the backend implementation technology.

This experiment provides practical evidence supporting **technology independence for the evaluated Processing Layer substitution**.

It does not imply universal technology independence or performance equivalence between Node.js/Express and Python/FastAPI.

---

## Experimental Evaluation

A physical MHUTEMP monitoring node was connected to the Stack 02 backend using the same:

- ESP32 acquisition hardware
- firmware
- sensing configuration
- WebSocket communication mechanism
- JSON message structure

used by the reference implementation.

During the evaluated continuous experimental session:

| Parameter | Result |
|---|---:|
| Test duration | 14 min 25 s |
| Persisted monitoring records | 421 |
| Median inter-record interval | 2.0 s |
| Processing backend | Python / FastAPI |
| Database | MongoDB |
| Acquisition node | ESP32 |
| Communication | WebSocket / HTTP |

The stored measurements were subsequently made available to the **Next.js monitoring interface**, preserving the end-to-end monitoring flow after the Processing Layer technology substitution.

---

## Technology Stack

- Python
- FastAPI
- Uvicorn
- MongoDB
- WebSocket
- HTTP / REST
- ESP32
- Next.js
- Railway

---

## Deployment

The Stack 02 backend is deployed on **Railway**:

https://mhutemp-s02-py-mon-production.up.railway.app/

The root endpoint provides the backend identification and operational status:

```json
{
  "system": "MHUTEMP",
  "stack": "02",
  "backend": "Python / FastAPI",
  "database": "MongoDB",
  "status": "running"
}
```

---

## Source Code

This repository contains the source code of the Stack 02 backend:

https://github.com/storres20/mhutemp-s02-py-mon

---

## Relationship with the MHUTEMP Experimental Stacks

Three technology configurations were considered in the architectural evaluation:

| Stack | Processing | Persistence | Experimental Purpose |
|---|---|---|---|
| Stack 01 | Node.js / Express | MongoDB | Operational baseline |
| **Stack 02** | **Python / FastAPI** | **MongoDB** | **Processing Layer substitution** |
| Stack 03 | Python / FastAPI | PostgreSQL | Persistence Layer substitution |

The comparisons are structured as follows:

```text
STACK 01
Node.js / Express
MongoDB
      |
      | Processing substitution
      v
STACK 02
Python / FastAPI
MongoDB
      |
      | Persistence substitution
      v
STACK 03
Python / FastAPI
PostgreSQL
```

Therefore:

- **Stack 01 → Stack 02** evaluates a selected substitution of the **Processing Layer** technology.
- **Stack 02 → Stack 03** evaluates a selected substitution of the **Persistence Layer** technology.

---

## Monitoring Information Flow Model

The MHUTEMP reference architecture is derived from a **Monitoring Information Flow Model (MIFM)**.

The model represents the transformation of monitoring information as:

```text
Physical Observation
        |
        v
Digital Measurement
        |
        v
Processed Information
        |
        v
Historical Record
        |
        v
Decision-Support Information
```

These stages are mapped to five architectural responsibilities:

```text
Acquisition
    |
    v
Communication
    |
    v
Processing
    |
    v
Persistence
    |
    v
Presentation
```

The architectural responsibilities are defined independently of the specific technologies used to implement them.

Stack 02 therefore represents one technology instantiation of this functional organization.

---

## Experimental Data

The experimental data associated with the technology-substitution and REST API evaluations have been deposited in **Zenodo**.

The dataset contains four CSV files corresponding to:

1. Stack 02 monitoring records
2. Stack 03 monitoring records
3. Stack 01 REST API request-level results
4. Stack 01 REST API summary results

These datasets support the reproducibility of the experiments reported in the associated research study.

---

## Scientific Context

This repository supports the reproducibility of the revised research study:

**MHUTEMP-ULT: An Open-Source IoT System for Ultra-Low Temperature Monitoring of Plasma Storage in Healthcare Facilities**

The study investigates whether the functional organization of the proposed reference software architecture can be preserved when selected implementation technologies are substituted.

Stack 02 specifically provides an alternative implementation of the **Processing Layer** using Python/FastAPI while retaining MongoDB persistence.

---

## Reproducibility Scope

The Stack 02 experiment demonstrates that the evaluated monitoring workflow can operate after substituting:

```text
Node.js / Express
       ↓
Python / FastAPI
```

while preserving MongoDB as the Persistence Layer and maintaining the expected monitoring information flow.

The experimental results should **not** be interpreted as:

- proof of universal technology independence;
- formal validation of modularity;
- formal validation of maintainability;
- proof of performance equivalence between Node.js/Express and Python/FastAPI;
- evidence that technology substitution requires no implementation effort;
- validation of scalability under arbitrary workloads.

The experiment specifically evaluates preservation of the proposed functional organization under the selected **Processing Layer technology substitution**.

---

## Related Repositories

### Stack 01 — Node.js/Express + MongoDB

https://github.com/storres20/bio-data-pro

### Stack 02 — Python/FastAPI + MongoDB

https://github.com/storres20/mhutemp-s02-py-mon

### Stack 03 — Python/FastAPI + PostgreSQL

https://github.com/storres20/mhutemp-s03-py-pg

---

## Author

**Italo Lon-Kan**

MHUTEMP Research Project  
Lima, Peru

---

## Citation

If you use this implementation in academic or research work, please cite the associated MHUTEMP-ULT study and repository.

```text
I. Lon-Kan, "mhutemp-s02-py-mon: MHUTEMP Stack 02
Python/FastAPI and MongoDB backend," GitHub repository, 2026.
```

---

## License

This repository is provided for **academic, research, and reproducibility purposes**.
