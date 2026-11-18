---
course: "بناء النماذج الأولية لمنتجات الذكاء الاصطناعي باستخدام وكلاء البرمجة"
code: "LDS-PRD-205"
version: "2027.1.0"
language: "ar"
view: "trainee"
source: "https://sdaiaacademy.github.io/lds-prd-205/index.html"
---

# بناء النماذج الأولية لمنتجات الذكاء الاصطناعي باستخدام وكلاء البرمجة

Prototyping AI Products with Coding Agents

مسار التنفيذيين والقادة · يومان تدريبيان + يوم للمشروع الختامي · 16 ساعة · المستوى 200

وجّه وكيل برمجة لبناء نموذج أولي يجيب عن سؤال منتج، بخطوات صغيرة وفحوصات، واختبره مع خمسة مستخدمين، وسلّم الفريق الهندسي ما تعلّمته لا الشيفرة

يوجّه العاملون في المنتجات والتصميم وكيل برمجة لبناء نموذج أولي لتطبيق ويب يستدعي نموذجًا مستضافًا على بيانات اصطناعية، ثم يضيفون فحوصات القبول، ويختبرونه مع خمسة مستخدمين، ويحددون المواضع التي تضلل فيها النماذج الأولية التي يبنيها الوكلاء، ويسلّمون الفريق الهندسي ما يُحتفظ به وما يُستبعد. أما الأدوات التي لا تحتاج إلى برمجة فيغطيها المقرر USE-FLU-205، والهندسة باستخدام الوكلاء يغطيها المقرر DEV-SWE-201.

**لمن هذا المقرر:** الممارسون. مديرو المنتجات ومالكوها، ومصممو الخدمات والتفاعل، وقادة التسليم ممن يتولون ميزات أو خدمات قائمة على الذكاء الاصطناعي، والمهندسون المنتقلون إلى أدوار المنتجات.

**الصيغة:** ورشة عمل: يومان مع مختبرات وعمل تحضيري موجه واختبار مع خمسة مستخدمين

## دراسة الحالة

**طيران قُبّرة: شارح تغيير الحجز.** طيران قُبّرة ناقل اقتصادي افتراضي، يريد فريق المنتج فيه أن يعرف هل تغني صفحة تشرح بالعربية رسوم تغيير الحجز وقاعدته عن الاتصال بمركز الاتصال. يبني المشاركون بوكيل برمجة «شارح تغيير الحجز»: الرسوم يحسبها البرنامج من قواعد الأجرة الثلاث، والشرح يكتبه نموذج مستضاف (وبديل مكتوب مسبقًا في الملفات). كل البيانات اصطناعية وثابتة: 6 حجوزات للعرض ثم 40 حجزًا، وأعداد تواصل لشهر، وخمس جلسات اختبار مسجلة، وحالة مرجعية لكل خطوة، ونسخة فيها ثمانية حدود مزروعة عمدًا لها مفتاح للمدرب.

## مخطط المقرر

### اليوم 1: من سؤال إلى نسخة أولى تعمل

الشرائح: https://sdaiaacademy.github.io/lds-prd-205/slides/day1.md

- **الجلسة 1: النموذج الأولي يجيب عن سؤال**
  - تصوغ سؤالًا يجيب عنه نموذج أولي في أيام، وتسمّي القرار الذي يتوقف عليه
  - تحدد ما يجب أن يكون حقيقيًا في النموذج الأولي وما يكفي أن يكون مزيفًا
  - تميّز النموذج الأولي من المشروع التجريبي ومن المنتج بما يثبته كل منها
  - [المختبر 1.1: كتابة الموجز (60 د)](https://sdaiaacademy.github.io/lds-prd-205/labs/D1_1_brief.html)
- **الجلسة 2: الموجز وملف السياق**
  - تفصل ما يبقى في الموجز عمّا يدخل ملف السياق
  - تكتب ملف سياق فيه التشغيل والبنية والقواعد وطريقة العمل
  - تراجع خطة الوكيل على الموجز قبل أن يكتب سطرًا
  - [المختبر 1.2: ملف السياق وخطة الوكيل (60 د)](https://sdaiaacademy.github.io/lds-prd-205/labs/D1_2_context_file.html)
- **الجلسة 3: خطوات صغيرة وإيداع لكل خطوة**
  - تطلب من الوكيل تغييرًا واحدًا وتتحقق منه بالتشغيل قبل الإيداع
  - تقرأ ما غيّره الوكيل من الفرق في Git دون أن تقرأ الشيفرة كلها
  - تتراجع عن تغيير كسر ما كان يعمل بأمر واحد
  - [المختبر 1.3: نسخة أولى بإيداع لكل خطوة (60 د)](https://sdaiaacademy.github.io/lds-prd-205/labs/D1_3_first_version.html)
- **الجلسة 4: بيئة معزولة ومفتاح محدود وبيانات اصطناعية**
  - تضع المفتاح في ملف البيئة وحده، وتحدّ الإنفاق وعدد الاستدعاءات
  - تطلب بيانات اصطناعية ثابتة تشبه الحالات الصعبة لا السهلة
  - تقسم العمل: الرقم يحسبه البرنامج، والشرح يكتبه النموذج
  - [المختبر 1.4: استدعاء النموذج والبيانات الاصطناعية (60 د)](https://sdaiaacademy.github.io/lds-prd-205/labs/D1_4_model_calls.html)

### اليوم 2: الحدود والتسليم

الشرائح: https://sdaiaacademy.github.io/lds-prd-205/slides/day2.md

- **الجلسة 1: أوهام المسار المثالي**
  - تجد الحالات التي لم يجربها العرض الأول
  - تكتب فحص قبول بالمعطى والفعل والمتوقع قبل أن يُبرمج
  - تعيد الفحوصات كلها بعد كل إصلاح وتسجل نتائجها
  - [المختبر 2.1: خمسة فحوصات قبول (60 د)](https://sdaiaacademy.github.io/lds-prd-205/labs/D2_1_acceptance_checks.html)
- **الجلسة 2: الأسرار والحزم والوصول والتراخيص**
  - تطبق قائمة تحقق الحدود بفحص آلي ثم باليد
  - تتحقق من مصدر كل ملف بيانات وترخيص كل أصل
  - ترتب الحدود بالأثر وتحدد لكل حد إصلاحه ومن يصلحه
  - [المختبر 2.2: قائمة تحقق الحدود (60 د)](https://sdaiaacademy.github.io/lds-prd-205/labs/D2_2_limits_checklist.html)
- **الجلسة 3: خمسة مستخدمين وما يحتفظ به المهندسون**
  - تدير جلسة اختبار قصيرة بمهمة واحدة وإفصاح عن الذكاء الاصطناعي
  - ترمّز ملاحظات خمس جلسات في نتائج معدودة تجيب عن السؤال
  - تفصل في التسليم التعلّم والمواصفات وحالات التقييم عن الشيفرة المستبعدة
  - [المختبر 2.3: اختبار مع خمسة مستخدمين (60 د)](https://sdaiaacademy.github.io/lds-prd-205/labs/D2_3_five_users.html)

### المشروع الختامي: المراجعة المباشرة مع المهندس

الشرائح: https://sdaiaacademy.github.io/lds-prd-205/slides/capstone.md

## المشروع الختامي

نموذج أولي لفكرة المشارك نفسه على بيانات اصطناعية، مع النتائج وحزمة تسليم يراجعها مهندس مراجعة مباشرة

**ما تسلّمه:** مشروع فردي يُسلَّم رابطًا لمجلد مشترك في Google Drive، فيه: الموجز وملف السياق، وحزمة Git للمستودع بكل إيداعاته (git bundle) وسجلات تفاعل الوكيل، وسجل الفحوصات، وقائمة الحدود المرتبة، وجدول نتائج الاختبار مع خمسة مستخدمين، وحزمة التسليم. بيانات اصطناعية فقط، ولا مفتاح في أي ملف. ثم تسع دقائق: خمس للعرض، وأربع يختار فيها المهندس إيداعًا يشرحه المشارك ويسأل عن الحزمة.

**سلم التقدير:**

- النموذج الأولي لفكرتك: يعمل على بيانات اصطناعية، وإيداع لكل خطوة عاملة: 20%
- سجل الفحوصات وقائمة الحدود المرتبة لنموذجك: 20%
- نتائج الاختبار مع خمسة مستخدمين بأدلتها: 25%
- حزمة التسليم: التعلّم والمواصفات وحالات التقييم منفصلة عن الشيفرة المستبعدة: 35%

## نواتج التعلم

- **LO1** يعدّ موجزًا وملف سياق يحددان السؤال والنطاق والبيانات والقيود ومعايير الإنجاز، استنادًا إلى فكرة الحالة ومواصفاتها (Applied) الدليل: موجز يبني الوكيل منه نسخة أولى عاملة
- **LO2** يستخدم وكيل برمجة لبناء نموذج أولي يستدعي نموذجًا لغويًا، بخطوات صغيرة متحقق منها وتحت إدارة الإصدارات، باستخدام بيئة عمل معزولة ومفتاح محدود الإنفاق وبيانات اصطناعية (Applied) الدليل: نموذج أولي يعمل وإيداع لكل خطوة عاملة
- **LO3** يختبر النموذج الأولي وفق فحوصات القبول وقائمة تحقق للحدود تشمل المسارات المضمّنة في الرموز البرمجية والأسرار المكشوفة والتبعيات غير المفحوصة والبيانات الحقيقية وإمكانية الوصول، على النموذج الأولي العامل (Applied) الدليل: سجل فحوصات وقائمة حدود مرتبة
- **LO4** يسلّم حزمة تسليم تفصل ما ثبت من تعلّم والمواصفات وحالات التقييم عن الرموز البرمجية الواجب استبعادها، استنادًا إلى نتائج الاختبار مع خمسة مستخدمين ومراجع هندسي (Performance) الدليل: حزمة تسليم تُقبل في مراجعة مباشرة

## الأدوات

- **وكيل برمجة:** goose, OpenCode, أي وكيل برمجة تجاري
- **بيئة عمل معزولة مع إدارة الإصدارات:** حاوية تطوير محلية مع Git, بيئة تطوير مستضافة بباقة مجانية
- **الوصول إلى نموذج مع حد للإنفاق:** نموذج مستضاف مفتوح الأوزان, أي واجهة برمجة تطبيقات (API) تجارية

## المتطلبات السابقة

- يملك خبرة سابقة في كتابة متطلبات منتج أو قصة مستخدم
- ينفذ أمرًا في الطرفية باتباع خطوات مكتوبة

## المصادر

### المرجعيات الوطنية

- [نظام حماية البيانات الشخصية](https://sdaia.gov.sa/ar/SDAIA/about/Documents/PersonalDataProtectionLawAr.pdf)
- [نظام حماية البيانات الشخصية: النص بتعديلاته (هيئة الخبراء بمجلس الوزراء)](https://laws.boe.gov.sa/BoeLaws/Laws/LawDetails/b7cfae89-828e-4994-b167-adaa00e37188/1)
- [Personal Data Protection Law (SDAIA, English edition)](https://sdaia.gov.sa/en/SDAIA/about/Documents/PersonalDataProtectionLaw.pdf)
- [مكتب إدارة البيانات الوطنية: سياسة تصنيف البيانات](https://sdaia.gov.sa/ar/SDAIA/about/Documents/DataClassificationPolicyAr.pdf)
- [NDMO: Data Classification Policy (English edition)](https://sdaia.gov.sa/en/SDAIA/about/Documents/DataClassificationPolicy.pdf)
- [سدايا: مبادئ الذكاء الاصطناعي التوليدي للجهات الحكومية (2025)](https://sdaia.gov.sa/ar/SDAIA/about/Files/GenAIGuidelinesForGovernmentARCompressed.pdf)
- [SDAIA: Generative AI Guidelines for Government (English edition)](https://sdaia.gov.sa/en/SDAIA/about/Files/GenAIGuidelinesForGovernmentENCompressed.pdf)
- [سدايا: مبادئ الذكاء الاصطناعي التوليدي للعموم (2025)](https://sdaia.gov.sa/ar/SDAIA/about/Files/GenerativeAIPublicAR.pdf)
- [SDAIA: Generative AI Guidelines for Public (English edition)](https://sdaia.gov.sa/en/SDAIA/about/Files/GenerativeAIPublicEN.pdf)
- [سدايا: الأنظمة والسياسات (صفحة الفهرس)](https://sdaia.gov.sa/ar/SDAIA/about/Pages/RegulationsAndPolicies.aspx)

### وكلاء البرمجة وملفات السياق

- [AGENTS.md: a README for agents](https://agents.md/)
- [goose: open source AI agent (Apache-2.0), repository README](https://github.com/aaif-goose/goose)
- [goose documentation: goose permission modes](https://goose-docs.ai/docs/guides/managing-tools/goose-permissions)
- [OpenCode documentation: permissions](https://opencode.ai/docs/permissions/)
- [Git documentation: git-restore](https://git-scm.com/docs/git-restore)
- [Git documentation: git-revert](https://git-scm.com/docs/git-revert)

### النماذج المستضافة والمفاتيح

- [OpenRouter documentation: API rate limits and free model variants](https://openrouter.ai/docs/api-reference/limits)
- [OpenRouter documentation: provisioning API keys with a credit limit](https://openrouter.ai/docs/features/provisioning-api-keys)

### الاختبار مع المستخدمين وإمكانية الوصول

- [Nielsen Norman Group: Why You Only Need to Test with 5 Users (2000)](https://www.nngroup.com/articles/why-you-only-need-to-test-with-5-users/)
- [W3C WCAG 2.2 source: Success Criterion 3.1.1 Language of Page](https://github.com/w3c/wcag/blob/main/guidelines/sc/20/language-of-page.html)
- [W3C WCAG 2.2 source: Success Criterion 3.3.2 Labels or Instructions](https://github.com/w3c/wcag/blob/main/guidelines/sc/20/labels-or-instructions.html)
- [W3C WCAG 2.2 source: Success Criterion 1.3.1 Info and Relationships](https://github.com/w3c/wcag/blob/main/guidelines/sc/20/info-and-relationships.html)

---

أكاديمية سدايا · مسار التنفيذيين والقادة · بناء النماذج الأولية لمنتجات الذكاء الاصطناعي باستخدام وكلاء البرمجة

إصدار المقرر 2027.1.0 · المحرّك 1.0.0 · بُني في ⁦2026-11-18⁩ · الإيداع b5b0f37
