---
permalink: /
title: ""
excerpt: ""
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

{% if site.google_scholar_stats_use_cdn %}
{% assign gsDataBaseUrl = "https://cdn.jsdelivr.net/gh/" | append: site.repository | append: "@" %}
{% else %}
{% assign gsDataBaseUrl = "https://raw.githubusercontent.com/" | append: site.repository | append: "/" %}
{% endif %}
{% assign url = gsDataBaseUrl | append: "google-scholar-stats/gs_data_shieldsio.json" %}

<span class='anchor' id='about-me'></span>

I received the B.E. degree from the Harbin Institute of Technology (HIT), Harbin, China in 2021. I got my Master’s degree at the Institute of Automation, Chinese Academy of Science (CASIA) in 2024, advised by Prof. [Jun Wan](http://www.cbsr.ia.ac.cn/users/jwan/), collaborate closely with Prof. [Zhen Lei](https://scholar.google.com/citations?user=cuJ3QG8AAAAJ&hl=zh-CN&oi=ao) (IEEE Fellow).
I used to be the research intern of the Foundation Model Group at Megvii Research, advised by [Xiangyu Zhang](https://scholar.google.com/citations?user=yuB-cfoAAAAJ&hl=en).
I'm currently working on technical exploration and application of multimodal foundation models in Kuaishou Technology.
My research interest includes Long-Tailed Learning, Foundation Model, Vision Language Model. I have published some papers at the top international AI conferences with total <a href='https://scholar.google.com/citations?user=93wHW4oAAAAJ'>google scholar citations <strong><span id='total_cit'></span></strong></a>. <a href='https://scholar.google.com/citations?user=93wHW4oAAAAJ'><img src="https://img.shields.io/endpoint?url={{ url | url_encode }}&logo=Google%20Scholar&labelColor=f6f6f6&color=9cf&style=flat&label=citations"></a>

Email: <a href="mailto:lijun9066@outlook.com">lijun9066@outlook.com</a>


# 🔥 News
- *2025.05*: 🎉🎉 One paper was accepted by TNNLS.
- *2025.03*: 🎉🎉 One paper was accepted by CVPR 2025.
- *2024.07*: I joined in Kuaishou Technology!
- *2024.03*: 🎉🎉 One paper was accepted by COLING 2024.
- *2023.12*: 🎉🎉 One paper was accepted by AAAI 2024.
- *2023.10*: 🎉🎉 One paper was accepted by PR.
- *2023.10*: 🎉🎉 One paper was accepted by TIP.
- *2023.01*: 🎉🎉 One paper was accepted by ICLR 2023. 
- *2022.12*: I serve as a reviewer for CVPR 2023.
- *2022.07*: I join the MEGVII Research as an Intern.
- *2022.03*: 🎉🎉 One paper was accepted by CVPR 2022.
- *2021.08*: I join National Laboratory of Pattern Recognition under the supervision of Prof. Jun Wan.


# 📝 Publications 

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">CVPR 2022</div><img src='images/CVPR.png' alt="sym" width="500" height="200"></div></div>
<div class='paper-box-text' markdown="1">

<big>**Nested Collaborative Learning for Long-Tailed Visual Recognition**</big><strong><span class='show_paper_citations' data='93wHW4oAAAAJ:UebtZRa9Y70C'></span></strong>

***Jun Li**\*, Zichang Tan\*, Jun Wan, Zhen Lei, Guodong Guo*


[[**PDF**]](https://openaccess.thecvf.com/content/CVPR2022/papers/Li_Nested_Collaborative_Learning_for_Long-Tailed_Visual_Recognition_CVPR_2022_paper.pdf)
[[**Project**]](https://github.com/Bazinga699/NCL)![](https://img.shields.io/github/forks/Bazinga699/NCL?logo=github)
![](https://img.shields.io/github/stars/Bazinga699/NCL)

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">ICLR 2023</div><img src='images/revcol.png' alt="sym" width="400" height="200"></div></div>
<div class='paper-box-text' markdown="1">

<big>**Reversible Column Networks**</big><strong><span class='show_paper_citations' data='93wHW4oAAAAJ:hqOjcs7Dif8C'></span></strong>


*Yuxuan Cai, Yizhuang Zhou, Qi Han, Jianjian Sun, Xiangwen Kong, **Jun Li**, Xiangyu Zhang*

[[**PDF**]](https://arxiv.org/pdf/2212.11696.pdf) [[**Introduction**]](https://zhuanlan.zhihu.com/p/607773400) [[**Project**]](https://github.com/megvii-research/RevCol)![](https://img.shields.io/github/forks/megvii-research/RevCol?logo=github)
![](https://img.shields.io/github/stars/megvii-research/RevCol)

</div>
</div>


<div class='paper-box'><div class='paper-box-image'><div><div class="badge">AAAI 2024 </div><img src='images/AAAI.png' alt="sym" width="500" height="200"></div></div>
<div class='paper-box-text' markdown="1">

<big>**Compound Text-Guided Prompt Tuning via Image-Adaptive Cues**</big><strong><span class='show_paper_citations' data='93wHW4oAAAAJ:8k81kl-MbHgC'></span></strong>

*Hao Tan\*, **Jun Li**\*,Yizhuang Zhou, Jun Wan, Zhen Lei, Xiangyu Zhang*



[[**PDF**]](https://arxiv.org/pdf/2312.06401.pdf)
[[**Project**]](https://github.com/EricTan7/TGP-T)![](https://img.shields.io/github/forks/EricTan7/TGP-T?logo=github)
![](https://img.shields.io/github/stars/EricTan7/TGP-T)

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">Pattern Recognition</div><img src='images/PR.png' alt="sym" width="400" height="200"></div></div>
<div class='paper-box-text' markdown="1">

<big>**NCL++: Nested Collaborative Learning for Long-Tailed Visual Recognition**</big><strong><span class='show_paper_citations' data='93wHW4oAAAAJ:0EnyYjriUFMC'></span></strong>

*Zichang Tan\*, **Jun Li**\*, Jinhao Du, Jun Wan, Zhen Lei, Guodong Guo*


[[**PDF**]](https://arxiv.org/pdf/2306.16709)
[[**Project**]](https://github.com/Bazinga699/NCL)![](https://img.shields.io/github/forks/Bazinga699/NCL?logo=github)
![](https://img.shields.io/github/stars/Bazinga699/NCL)

</div>
</div>

<div class='paper-box'><div class='paper-box-image'><div><div class="badge">TIP</div><img src='images/TIP.png' alt="sym" width="500" height="200"></div></div>
<div class='paper-box-text' markdown="1">

<big>**General vs. Long-Tailed Age Estimation: An Approach to Kill Two Birds with One Stone**</big>

*Zenghao Bao, Zichang Tan, **Jun Li**, Jun Wan, Xibo Ma, Zhen Lei*



[[**PDF**]](http://arxiv.org/abs/2307.10129)
[[**Project**]]()

</div>
</div>

- \* indicates equal contribution.

# 🎖 Honors and Awards
- *2022.12*  National Scholarship.
- *2021.06* Outstanding Graduates of Harbin Institute of Technology.
- *2021.05* New Engineering Program Design Ability Examination (Level A), Rank 1/2280.
- *2019.08*  National First Prize in the National College Student "NXP Cup" Intelligent Vehicle Contest. Experience Sharing Posted on ![](https://img.shields.io/badge/dynamic/json?color=ff69b4&label=bilibili&query=data.stat.view&url=https%3A%2F%2Fapi.bilibili.com%2Fx%2Fweb-interface%2Fview%3Fbvid%3DBV1Ft4y1i79A) [Link](https://www.bilibili.com/video/BV1Ft4y1i79A/?vd_source=3168e87544c9e17f675d9261e8440f87).
- *2019.12* First Prize in the Heilongjiang Province Division of the National College Student Mathematical Modeling Competition.
- *2016.11* National Olympiad in Informatics in Provinces (NOIP) - Advanced Group, Second Prize.



# 📖 Educations
- *2021.08 - 2024.07*, <img src='images/CASIA2.png' width="30" height="30" />Institute of Automation, Chinese Academy of Science (CASIA), Beijing, China.
- *2017.08 - 2021.06*, <img src='images/HIT.png' width="30" height="30" />Harbin Institute of Technology (HIT), Harbin, China.

# 💬 Talks
- *2022.12*, presentation on the paper "Nested Collaborative Learning for Long-Tailed Visual Recognition" at VALSE2022.



# 💻 Internships
- *2022.07 - 2023.12*, <img src='images/megvii.png' width="60" height="20" /> Algorithm Intern, advisor: [Xiangyu Zhang](https://scholar.google.com/citations?user=yuB-cfoAAAAJ&hl=en)
