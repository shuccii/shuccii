<div align="center">

<img width="100%" alt="Repository telemetry" src="assets/jarvis-header.svg" />

<!-- ─── navigation ─────────────────────────────────────────────── -->

[![Research](https://img.shields.io/badge/01-RESEARCH-5FD8F2?style=flat-square&labelColor=040F18)](#-01--research) [![Method](https://img.shields.io/badge/02-METHOD-5FD8F2?style=flat-square&labelColor=040F18)](#-02--method) [![Stack](https://img.shields.io/badge/03-STACK-5FD8F2?style=flat-square&labelColor=040F18)](#-03--stack) [![Activity](https://img.shields.io/badge/04-ACTIVITY-5FD8F2?style=flat-square&labelColor=040F18)](#-04--activity) [![Repositories](https://img.shields.io/badge/05-REPOSITORIES-E8B455?style=flat-square&labelColor=040F18)](#-05--repositories) [![Site](https://img.shields.io/badge/↗-shuccii.github.io-E8B455?style=flat-square&labelColor=040F18)](https://shuccii.github.io)

<img width="100%" alt="git readout" src="assets/command-strip.svg" />

<img width="100%" alt="" src="assets/divider.svg" />

</div>

## ◤ 01 · RESEARCH

M.S. student at **NAIST**, working on machine-learning property prediction for **fusion reactor structural materials** — reduced-activation ferritic/martensitic steels, tungsten, and other materials that have to survive neutron irradiation at high temperature.

The constraint that shapes everything: irradiation experiments are slow and expensive, so each property has only a handful of measurements. The work is therefore less about bigger models and more about **making scarce experiments talk to abundant computation** — data assimilation, transfer and multi-task learning, multi-fidelity modelling, and uncertainty quantification.

Currently extending into privacy-preserving and federated learning, for materials data that cannot leave the institution that measured it.

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ 02 · METHOD

```mermaid
%%{init: {'theme':'base','themeVariables':{'background':'#040f18','primaryColor':'#0a2735','primaryTextColor':'#cfeefb','primaryBorderColor':'#5fd8f2','lineColor':'#3f7f96','fontFamily':'monospace','fontSize':'14px'}}}%%
flowchart LR
    A["EXPERIMENT<br/><small>few · expensive</small>"]:::src --> D
    B["FIRST-PRINCIPLES<br/><small>DFT</small>"]:::src --> D
    C["SIMULATION<br/><small>MD / phase-field</small>"]:::src --> D
    D["DATA ASSIMILATION<br/><small>covariance linkage</small>"]:::core --> E
    E["PREDICTION<br/><small>property + uncertainty</small>"]:::out --> F
    F["BAYESIAN OPT<br/><small>next experiment</small>"]:::gold --> A

    classDef src  fill:#08202c,stroke:#3f7f96,stroke-width:1px,color:#cfeefb
    classDef core fill:#0c3346,stroke:#5fd8f2,stroke-width:1.5px,color:#f2fdff
    classDef out  fill:#08202c,stroke:#5fd8f2,stroke-width:1px,color:#cfeefb
    classDef gold fill:#241a06,stroke:#e8b455,stroke-width:1.5px,color:#f0d9a8
```

> Sparse experiments cannot cover a high-dimensional composition space on their own.
> Linked to abundant computation through a shared covariance structure, they can tell you which single experiment to run next.

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ 03 · STACK

<div align="center">

![Python](https://img.shields.io/badge/Python-5FD8F2?style=flat-square&logo=python&logoColor=5FD8F2&labelColor=040F18) ![PyTorch](https://img.shields.io/badge/PyTorch-5FD8F2?style=flat-square&logo=pytorch&logoColor=5FD8F2&labelColor=040F18) ![scikit-learn](https://img.shields.io/badge/scikit--learn-5FD8F2?style=flat-square&logo=scikitlearn&logoColor=5FD8F2&labelColor=040F18) ![NumPy](https://img.shields.io/badge/NumPy-5FD8F2?style=flat-square&logo=numpy&logoColor=5FD8F2&labelColor=040F18) ![pandas](https://img.shields.io/badge/pandas-5FD8F2?style=flat-square&logo=pandas&logoColor=5FD8F2&labelColor=040F18) ![SciPy](https://img.shields.io/badge/SciPy-5FD8F2?style=flat-square&logo=scipy&logoColor=5FD8F2&labelColor=040F18)

![Jupyter](https://img.shields.io/badge/Jupyter-3F7F96?style=flat-square&logo=jupyter&logoColor=3F7F96&labelColor=040F18) ![Matplotlib](https://img.shields.io/badge/Matplotlib-3F7F96?style=flat-square&logo=plotly&logoColor=3F7F96&labelColor=040F18) ![LaTeX](https://img.shields.io/badge/LaTeX-3F7F96?style=flat-square&logo=latex&logoColor=3F7F96&labelColor=040F18) ![Astro](https://img.shields.io/badge/Astro-3F7F96?style=flat-square&logo=astro&logoColor=3F7F96&labelColor=040F18) ![Git](https://img.shields.io/badge/Git-E8B455?style=flat-square&logo=git&logoColor=E8B455&labelColor=040F18) ![Linux](https://img.shields.io/badge/Linux-3F7F96?style=flat-square&logo=linux&logoColor=3F7F96&labelColor=040F18)

</div>

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ 04 · ACTIVITY

<div align="center">

<img width="98%" alt="account summary" src="assets/cards/profile-details.svg" />

<img width="45%" alt="languages by repository" src="assets/cards/repos-per-language.svg" />
<img width="45%" alt="languages by commit" src="assets/cards/most-commit-language.svg" />

<img width="45%" alt="totals" src="assets/cards/stats.svg" />
<img width="45%" alt="commits by hour" src="assets/cards/productive-time.svg" />

<br/>

<img width="100%" alt="contribution grid" src="https://raw.githubusercontent.com/shuccii/shuccii/output/github-snake.svg" />

</div>

<div align="center"><img width="100%" alt="" src="assets/divider.svg" /></div>

## ◤ 05 · REPOSITORIES

| | Repository | Contents |
| :---: | :--- | :--- |
| `01` | **[Python-seminar](https://github.com/shuccii/Python-seminar)** | Lab seminar notebooks — regression, SVR, classification, clustering, PCA, and the reasoning behind each. |
| `02` | **[shuccii.github.io](https://github.com/shuccii/shuccii.github.io)** | Personal site — research notes and writing. Astro. |
| `03` | **[shuccii](https://github.com/shuccii/shuccii)** | This profile. The panels above are redrawn from the GitHub API every day by Actions. |

<div align="center">

<img width="100%" alt="" src="assets/jarvis-footer.svg" />

</div>
