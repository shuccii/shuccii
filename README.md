<div align="center">

<img width="100%" alt="J.A.R.V.I.S. interface" src="assets/jarvis-header.svg" />

<img width="100%" alt="boot sequence" src="assets/boot-sequence.svg" />

<p>
  <a href="https://shuccii.github.io"><img alt="Website" src="https://img.shields.io/badge/UPLINK-shuccii.github.io-22D3EE?style=for-the-badge&logo=astro&logoColor=22D3EE&labelColor=05090F" /></a>
  <a href="https://github.com/shuccii?tab=repositories"><img alt="Repositories" src="https://img.shields.io/badge/ARCHIVE-repositories-F5B841?style=for-the-badge&logo=github&logoColor=F5B841&labelColor=05090F" /></a>
  <img alt="Reactor" src="https://img.shields.io/badge/REACTOR-fusion%20materials-E62429?style=for-the-badge&logo=atom&logoColor=E62429&labelColor=05090F" />
  <img alt="Visitors" src="https://komarev.com/ghpvc/?username=shuccii&style=for-the-badge&color=22D3EE&label=SCANS" />
</p>

<img width="100%" alt="" src="assets/divider.svg" />

</div>

## ◤ MISSION PROFILE

```console
jarvis@stark:~$ whoami --verbose

  OPERATOR ....... Shuichi Tani  (谷 周一)
  FACILITY ....... NAIST — Nara Institute of Science and Technology
  DIVISION ....... Materials Science × Information Science
  OBJECTIVE ...... ML-driven property prediction for fusion reactor materials
  THREAT ......... data scarcity — neutron irradiation experiments are slow & costly
  COUNTERMEASURE . heterogeneous data assimilation across experiment / DFT / simulation
  STATUS ......... ● ACTIVE
```

- **⚛️ Primary mission** — structural materials that survive a fusion reactor: reduced-activation ferritic/martensitic steels, tungsten, and their behaviour under neutron irradiation and high temperature.
- **🛡️ Core problem** — you cannot brute-force this with data. Irradiation campaigns are expensive, so every property has only a handful of measurements.
- **🔗 My approach** — fuse the scarce experiments with abundant first-principles and simulation data through a shared covariance structure, so the calculations carry the experiments into unexplored composition space.
- **📡 Currently calibrating** — uncertainty quantification, multi-task learning, and privacy-preserving / federated ML for materials data shared across institutions.
- **📍 Base of operations** — Nara, Japan.

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ TARGETING SYSTEM

```mermaid
%%{init: {'theme':'base','themeVariables':{'background':'#05090f','primaryColor':'#0b2733','primaryTextColor':'#e6feff','primaryBorderColor':'#22d3ee','lineColor':'#f5b841','fontFamily':'monospace','fontSize':'15px'}}}%%
flowchart LR
    A["🧪 EXPERIMENT<br/>few · expensive"]:::exp --> D
    B["⚛️ FIRST-PRINCIPLES<br/>DFT"]:::calc --> D
    C["🖥️ SIMULATION<br/>MD / phase-field"]:::calc --> D
    D["🔗 DATA ASSIMILATION<br/>covariance linkage"]:::core --> E
    E["📈 PREDICTION<br/>property + uncertainty"]:::out --> F
    F["🎯 BAYESIAN OPT<br/>next target acquired"]:::gold --> A

    classDef exp  fill:#0b2733,stroke:#22d3ee,stroke-width:2px,color:#e6feff
    classDef calc fill:#0b2733,stroke:#0e7490,stroke-width:2px,color:#bfe9f5
    classDef core fill:#103a4a,stroke:#67e8f9,stroke-width:3px,color:#eaffff
    classDef out  fill:#0b2733,stroke:#22d3ee,stroke-width:2px,color:#e6feff
    classDef gold fill:#2b1f06,stroke:#f5b841,stroke-width:3px,color:#ffe9a8
```

> **The loop is the point.** Sparse experiments alone cannot cover a high-dimensional composition space —
> but linked to abundant computation, they can tell you which single experiment to run next.

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ SUIT SPECIFICATIONS

<div align="center">

<img alt="Python" src="https://img.shields.io/badge/Python-22D3EE?style=for-the-badge&logo=python&logoColor=22D3EE&labelColor=05090F" />
<img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-F5B841?style=for-the-badge&logo=pytorch&logoColor=F5B841&labelColor=05090F" />
<img alt="scikit-learn" src="https://img.shields.io/badge/scikit--learn-22D3EE?style=for-the-badge&logo=scikitlearn&logoColor=22D3EE&labelColor=05090F" />
<img alt="NumPy" src="https://img.shields.io/badge/NumPy-F5B841?style=for-the-badge&logo=numpy&logoColor=F5B841&labelColor=05090F" />
<img alt="pandas" src="https://img.shields.io/badge/pandas-22D3EE?style=for-the-badge&logo=pandas&logoColor=22D3EE&labelColor=05090F" />
<br/>
<img alt="SciPy" src="https://img.shields.io/badge/SciPy-F5B841?style=for-the-badge&logo=scipy&logoColor=F5B841&labelColor=05090F" />
<img alt="Jupyter" src="https://img.shields.io/badge/Jupyter-22D3EE?style=for-the-badge&logo=jupyter&logoColor=22D3EE&labelColor=05090F" />
<img alt="Matplotlib" src="https://img.shields.io/badge/Matplotlib-F5B841?style=for-the-badge&logo=plotly&logoColor=F5B841&labelColor=05090F" />
<img alt="LaTeX" src="https://img.shields.io/badge/LaTeX-22D3EE?style=for-the-badge&logo=latex&logoColor=22D3EE&labelColor=05090F" />
<img alt="Astro" src="https://img.shields.io/badge/Astro-F5B841?style=for-the-badge&logo=astro&logoColor=F5B841&labelColor=05090F" />
<br/>
<img alt="Git" src="https://img.shields.io/badge/Git-E62429?style=for-the-badge&logo=git&logoColor=E62429&labelColor=05090F" />
<img alt="VS Code" src="https://img.shields.io/badge/VS_Code-22D3EE?style=for-the-badge&logo=visualstudiocode&logoColor=22D3EE&labelColor=05090F" />
<img alt="Linux" src="https://img.shields.io/badge/Linux-F5B841?style=for-the-badge&logo=linux&logoColor=F5B841&labelColor=05090F" />
<img alt="macOS" src="https://img.shields.io/badge/macOS-22D3EE?style=for-the-badge&logo=apple&logoColor=22D3EE&labelColor=05090F" />

</div>

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ SYSTEM DIAGNOSTICS

<div align="center">

<img width="98%" alt="operator telemetry" src="assets/cards/profile-details.svg" />

<img width="45%" alt="language distribution" src="assets/cards/repos-per-language.svg" />
<img width="45%" alt="commit distribution" src="assets/cards/most-commit-language.svg" />

<img width="45%" alt="repository stats" src="assets/cards/stats.svg" />
<img width="45%" alt="active hours" src="assets/cards/productive-time.svg" />

</div>

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ PERIMETER SCAN

<div align="center">

<img width="100%" alt="contribution grid scan" src="https://raw.githubusercontent.com/shuccii/shuccii/output/github-snake.svg" />

<sub>`arc-reactor palette` — the drone sweeps the contribution grid once every 24 hours.</sub>

</div>

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ ACTIVE PROJECTS

| ID | Designation | Payload |
| :---: | :--- | :--- |
| `01` | **[Python-seminar](https://github.com/shuccii/Python-seminar)** | Lab seminar notebooks — regression, SVR, classification, clustering, PCA, and the reasoning behind each. |
| `02` | **[shuccii.github.io](https://github.com/shuccii/shuccii.github.io)** | Personal uplink. Research notes and writing, built with Astro. |

<div align="center">

<img width="100%" alt="" src="assets/divider.svg" />

<sub>`> J.A.R.V.I.S.: Few experiments, many calculations. The model lives in between.`</sub>

<br/>

<img width="100%" alt="" src="assets/jarvis-footer.svg" />

</div>
