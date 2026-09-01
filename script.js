const renderIcons = () => {
  if (window.lucide) {
    window.lucide.createIcons();
  }
};

const navItems = document.querySelectorAll(".nav-item");
const mobileMenu = document.querySelector(".mobile-menu");
const commandInput = document.querySelector("#commandInput");
const commandButton = document.querySelector("#commandButton");
const chatInput = document.querySelector("#chatInput");
const chatButton = document.querySelector("#chatButton");
const chatPanel = document.querySelector(".chat-panel");
const roleCards = document.querySelectorAll("[data-role]");
const roleCopyTargets = document.querySelectorAll("[data-role-copy]");
const authViews = document.querySelectorAll("[data-auth-view]");
const authBack = document.querySelector("[data-auth-back]");
const loginForm = document.querySelector(".login-view");
const loginCopyTargets = document.querySelectorAll("[data-login-copy]");
const loginAccount = document.querySelector("[data-login-field='account']");
const logoutButton = document.querySelector("[data-logout]");
const roleVisibleItems = document.querySelectorAll("[data-visible-role]");
const taskCards = document.querySelectorAll("[data-task-card]");
const assignmentOptions = document.querySelectorAll("[data-assignment-option]");
const assignmentPublish = document.querySelector("[data-assignment-publish]");
const assignmentStatus = document.querySelector("[data-assignment-status]");
const scrollButtons = document.querySelectorAll("[data-scroll-target]");
const runCodeButtons = document.querySelectorAll("[data-run-code], [data-submit-code]");
const studentCode = document.querySelector("#studentCode");
const customTestInput = document.querySelector("#customTestInput");
const customExpectedOutput = document.querySelector("#customExpectedOutput");
const customResult = document.querySelector("[data-custom-result]");
const diagnosisStatus = document.querySelector("[data-diagnosis-status]");
const passCount = document.querySelector("[data-pass-count]");
const weakPoint = document.querySelector("[data-weak-point]");
const nextHint = document.querySelector("[data-next-hint]");
const assistantThread = document.querySelector("[data-assistant-thread]");
const assistantInput = document.querySelector("#assistantInput");
const assistantSend = document.querySelector("[data-assistant-send]");
const policySave = document.querySelector("[data-policy-save]");
const policyStatus = document.querySelector("[data-policy-status]");
const knowledgeNodes = document.querySelectorAll("[data-knowledge-node]");
const domainSave = document.querySelector("[data-domain-save]");
const domainStatus = document.querySelector("[data-domain-status]");
const studentSelectors = document.querySelectorAll("[data-student-selector]");
const latestStatus = document.querySelector("[data-latest-status]");
const latestTitle = document.querySelector("[data-latest-title]");
const latestSummary = document.querySelector("[data-latest-summary]");
const masteryDelta = document.querySelector("[data-mastery-delta]");
const errorProfile = document.querySelector("[data-error-profile]");
const nextAction = document.querySelector("[data-next-action]");
const teachingSave = document.querySelector("[data-teaching-save]");
const teachingStatus = document.querySelector("[data-teaching-status]");
const weightSliders = document.querySelectorAll("[data-weight-slider]");
const agentStatus = document.querySelector("[data-agent-status]");
const agentTask = document.querySelector("[data-agent-task]");
const agentReason = document.querySelector("[data-agent-reason]");
const agentRag = document.querySelector("[data-agent-rag]");
const agentTool = document.querySelector("[data-agent-tool]");
const agentEval = document.querySelector("[data-agent-eval]");
const agentOutput = document.querySelector("[data-agent-output]");

const AGENT_API_BASE = window.ITS_AGENT_API_BASE || "http://localhost:8000";

let selectedRole = "teacher";

const roleCopy = {
  teacher: {
    pageTitle: "教师工作台",
    roleBadge: "教师端",
    userName: "林老师",
    welcomeTitle: "下午好，林老师 · 今天继续点亮每个学生",
    welcomeDesc:
      "你有 3 个 Python 学习空间、6 位 AI 助教待命，系统已整理好今日薄弱点、待发练习和课堂流程。",
  },
  student: {
    pageTitle: "学生学习台",
    roleBadge: "学生端",
    userName: "林同学",
    welcomeTitle: "下午好，林同学 · 今天继续拆解每一道 Python 难题",
    welcomeDesc:
      "你有 3 个待完成练习、2 个薄弱知识点需要复习，Python 智能小助手会用提问陪你推进。",
  },
};

const loginCopy = {
  teacher: {
    eyebrow: "Teacher Login",
    title: "教师登录",
    description: "登录后可查看班级数据、管理教学内容、发放练习并配置智能小助手规范。",
    account: "teacher@its.local",
    permissionTitle: "教师端权限",
    permissions: [
      "查看所有学生学习数据与诊断报告",
      "管理知识点、题库、测试用例和教学资源",
      "发放练习并配置 Python 智能小助手规范",
    ],
    button: "进入教师工作台",
  },
  student: {
    eyebrow: "Student Login",
    title: "学生登录",
    description: "登录后可进入练习中心、查看个人诊断反馈，并使用苏格拉底式 Python 智能小助手。",
    account: "student@its.local",
    permissionTitle: "学生端权限",
    permissions: [
      "完成教师发放或系统推荐的 Python 练习",
      "查看个人知识掌握度、错题与诊断反馈",
      "使用智能小助手进行引导式提问和复习",
    ],
    button: "进入学生学习台",
  },
};

const showAuthView = (viewName) => {
  authViews.forEach((view) => {
    view.hidden = view.dataset.authView !== viewName;
  });
};

const updateLoginView = (role) => {
  const copy = loginCopy[role] ?? loginCopy.teacher;

  loginCopyTargets.forEach((target) => {
    const key = target.dataset.loginCopy;

    if (key === "permissions") {
      target.replaceChildren(
        ...copy.permissions.map((item) => {
          const li = document.createElement("li");
          li.textContent = item;
          return li;
        }),
      );
      return;
    }

    if (copy[key]) {
      target.textContent = copy[key];
    }
  });

  if (loginAccount) {
    loginAccount.value = copy.account;
  }
};

const syncRoleVisibility = (role) => {
  roleVisibleItems.forEach((item) => {
    item.hidden = item.dataset.visibleRole !== role;
  });
};

const syncActiveNav = (role) => {
  const defaultSection = role === "student" ? "student-tasks" : "analytics";
  const defaultItem = document.querySelector(`[data-section="${defaultSection}"]`);

  if (!defaultItem) return;

  navItems.forEach((item) => item.classList.remove("active"));
  defaultItem.classList.add("active");
};

const enterWorkspace = (role) => {
  const copy = roleCopy[role] ?? roleCopy.teacher;

  roleCopyTargets.forEach((target) => {
    const key = target.dataset.roleCopy;
    if (copy[key]) {
      target.textContent = copy[key];
    }
  });

  document.body.classList.remove("auth-gated");
  document.body.dataset.role = role;
  syncRoleVisibility(role);
  syncActiveNav(role);
  document.querySelector("#home")?.scrollIntoView({ block: "start" });
  renderIcons();
};

const resetWorkspace = () => {
  document.body.classList.add("auth-gated");
  delete document.body.dataset.role;
  selectedRole = "teacher";
  updateLoginView(selectedRole);
  showAuthView("role");
  syncRoleVisibility(selectedRole);
  syncActiveNav(selectedRole);
  renderIcons();
};

navItems.forEach((item) => {
  item.addEventListener("click", () => {
    navItems.forEach((nav) => nav.classList.remove("active"));
    item.classList.add("active");
    document.body.classList.remove("nav-open");

    const target = document.querySelector(`#${item.dataset.section}`);
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

mobileMenu?.addEventListener("click", () => {
  document.body.classList.toggle("nav-open");
});

document.addEventListener("click", (event) => {
  const isSidebar = event.target.closest(".sidebar");
  const isMenu = event.target.closest(".mobile-menu");

  if (!isSidebar && !isMenu) {
    document.body.classList.remove("nav-open");
  }
});

const renderAgentResponse = (data) => {
  const taskLabel =
    data.route.task_type === "exercise_generation" ? "练习题生成" : "结构化教案生成";
  const sources = data.retrieved_documents
    .map((doc) => `${doc.id} · ${doc.title}`)
    .join("\n");
  const outputSummary =
    data.output.type === "exercise_set"
      ? data.output.exercises
          .map((item) => `${item.level}档：${item.title}｜${item.diagnosis_focus.join("、")}`)
          .join("\n")
      : data.output.lesson_flow
          .map((item) => `${item.stage} ${item.minutes}分钟：${item.activity}`)
          .join("\n");

  if (agentStatus) {
    agentStatus.textContent = data.llm_used
      ? `已调用真实大模型：${data.llm_model}`
      : "已完成 Mock 演示：配置 OPENAI_API_KEY 后调用真实大模型";
  }
  if (agentTask) agentTask.textContent = `${taskLabel} · 置信度 ${data.route.confidence}`;
  if (agentReason) agentReason.textContent = data.route.reason;
  if (agentRag) agentRag.textContent = `${data.retrieved_documents.length} 条`;
  if (agentTool) agentTool.textContent = data.tool_name;
  if (agentEval) {
    agentEval.textContent = `工具成功：${data.evaluation_record.tool_success ? "是" : "否"}；已记录 run_id ${data.run_id.slice(0, 8)}`;
  }
  if (agentOutput) {
    agentOutput.textContent = [
      `标题：${data.output.title}`,
      "",
      "RAG 来源：",
      sources,
      "",
      "结构化输出：",
      outputSummary,
    ].join("\n");
  }
};

const runTeachingAgent = async (request) => {
  if (!agentStatus || !agentOutput) return;

  agentStatus.textContent = "Agent 正在识别任务、检索知识库并生成结果...";
  agentOutput.textContent = "请求后端中...";

  try {
    const response = await fetch(`${AGENT_API_BASE}/api/agent/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        teacher_request: request,
        class_profile: "Python A 班，学生有基础，准备做项目/算法题，近期薄弱点集中在边界条件和复杂度分析。",
        top_k: 4,
      }),
    });

    if (!response.ok) {
      const detail = await response.text();
      throw new Error(detail || `HTTP ${response.status}`);
    }

    const data = await response.json();
    renderAgentResponse(data);
  } catch (error) {
    agentStatus.textContent = "后端未连接";
    agentOutput.textContent = [
      "没有拿到 FastAPI 后端响应。",
      "",
      "请在项目根目录运行：",
      "uvicorn backend.app.main:app --reload --port 8000",
      "",
      `错误信息：${error.message}`,
    ].join("\n");
  }
};

commandButton?.addEventListener("click", async () => {
  const request = commandInput.value.trim() || "生成今日教学任务";
  commandInput.value = request;
  commandButton.classList.add("is-done");
  commandButton.disabled = true;

  if (document.body.dataset.role === "teacher") {
    await runTeachingAgent(request);
  } else {
    commandInput.value = `${request} · 已加入学习任务`;
  }

  window.setTimeout(() => {
    commandButton.classList.remove("is-done");
    commandButton.disabled = false;
  }, 1400);
});

commandInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    commandButton?.click();
  }
});

taskCards.forEach((card) => {
  card.addEventListener("click", () => {
    taskCards.forEach((item) => item.classList.remove("selected"));
    card.classList.add("selected");
  });
});

assignmentOptions.forEach((option) => {
  option.addEventListener("click", () => {
    assignmentOptions.forEach((item) => item.classList.remove("active"));
    option.classList.add("active");
  });
});

assignmentPublish?.addEventListener("click", () => {
  if (!assignmentStatus) return;

  assignmentStatus.textContent = "已发布：Python A 班将收到个性化练习，教师端看板已创建跟踪任务。";
  assignmentStatus.classList.add("is-done");
});

scrollButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.querySelector(`#${button.dataset.scrollTarget}`);
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

const normalizeCaseInput = (value) => {
  const trimmed = value.trim();
  if (!trimmed) return "";

  const quoted =
    (trimmed.startsWith("\"") && trimmed.endsWith("\"")) ||
    (trimmed.startsWith("'") && trimmed.endsWith("'"));

  return (quoted ? trimmed.slice(1, -1) : trimmed)
    .replaceAll("\\n", "\n")
    .replaceAll("\\\"", "\"")
    .replaceAll("\\'", "'");
};

const longestSubstringLength = (input) => {
  let left = 0;
  let best = 0;
  const seen = new Map();

  [...input].forEach((ch, right) => {
    if (seen.has(ch)) {
      left = Math.max(left, seen.get(ch) + 1);
    }
    seen.set(ch, right);
    best = Math.max(best, right - left + 1);
  });

  return best;
};

const simulatedStudentOutput = (input) => {
  const code = studentCode?.value ?? "";
  const usesGuardedLeftUpdate =
    /left\s*=\s*max\s*\(\s*left\s*,\s*seen\s*\[\s*ch\s*\]\s*\+\s*1\s*\)/.test(code) ||
    /left\s*=\s*max\s*\(\s*seen\s*\[\s*ch\s*\]\s*\+\s*1\s*,\s*left\s*\)/.test(code);

  if (usesGuardedLeftUpdate) {
    return longestSubstringLength(input);
  }

  let left = 0;
  let best = 0;
  const seen = new Map();

  [...input].forEach((ch, right) => {
    if (seen.has(ch)) {
      left = seen.get(ch) + 1;
    }
    seen.set(ch, right);
    best = Math.max(best, right - left + 1);
  });

  return best;
};

const evaluateCodingSubmission = () => {
  const fixedCases = [
    { input: "abcabcbb", expected: 3 },
    { input: "", expected: 0 },
    { input: "bbbbb", expected: 1 },
    { input: "abba", expected: 2 },
  ];
  const passedFixed = fixedCases.filter((item) => simulatedStudentOutput(item.input) === item.expected).length;
  const rawInput = customTestInput?.value ?? "abba";
  const customInput = normalizeCaseInput(rawInput);
  const standardExpected = longestSubstringLength(customInput);
  const expectedText = customExpectedOutput?.value.trim();
  const expected = expectedText ? Number(expectedText) : standardExpected;
  const output = simulatedStudentOutput(customInput);
  const customPassed = Number.isFinite(expected) && output === expected;

  if (customExpectedOutput && !expectedText) {
    customExpectedOutput.value = String(standardExpected);
  }

  if (customResult) {
    customResult.classList.toggle("is-pass", customPassed);
    customResult.classList.toggle("is-fail", !customPassed);
    customResult.textContent = customPassed
      ? `自定义用例通过：s="${customInput}"，程序输出 ${output}。`
      : `自定义用例未通过：s="${customInput}"，程序输出 ${output}，预期 ${expected}。`;
  }

  if (!diagnosisStatus) return;

  diagnosisStatus.classList.add("is-success");
  diagnosisStatus.querySelector("strong").textContent = `固定用例通过 ${passedFixed}/4，自定义${
    customPassed ? "通过" : "未通过"
  }`;

  const hasBoundaryRisk = passedFixed < fixedCases.length || !customPassed;
  diagnosisStatus.querySelector("p").textContent = hasBoundaryRisk
    ? `当前输入 s="${customInput}" 的输出为 ${output}。如果 abba 一类用例失败，通常说明重复字符出现在当前窗口左侧时 left 被回退，请思考 left 更新时是否需要取 max。`
    : `当前输入 s="${customInput}" 的输出为 ${output}，固定用例也全部通过。可以继续提交诊断或尝试更复杂的自定义输入。`;

  if (passCount) passCount.textContent = `${passedFixed}/4`;
  if (weakPoint) weakPoint.textContent = hasBoundaryRisk ? "滑动窗口左边界" : "暂无明显薄弱点";
  if (nextHint) {
    nextHint.textContent = hasBoundaryRisk
      ? "比较 left 和 seen[ch] + 1 的大小"
      : "尝试构造更长重复字符用例";
  }

  if (latestStatus) latestStatus.textContent = "已同步";
  if (latestTitle) latestTitle.textContent = `最长无重复子串 · 通过 ${passedFixed}/4`;
  if (latestSummary) {
    latestSummary.textContent = hasBoundaryRisk
      ? "诊断模型定位为边界错误，关联知识点：滑动窗口左边界、字典 last index 更新。"
      : "本次固定用例和自定义用例均通过，学生模型将暂时提高滑动窗口掌握度。";
  }
  if (masteryDelta) masteryDelta.textContent = hasBoundaryRisk ? "滑动窗口 -0.03" : "滑动窗口 +0.04";
  if (errorProfile) errorProfile.textContent = hasBoundaryRisk ? "边界错误 +1" : "暂无新增错误";
  if (nextAction) nextAction.textContent = hasBoundaryRisk ? "补做窗口左边界专项" : "进入滑动窗口挑战题";
};

runCodeButtons.forEach((button) => {
  button.addEventListener("click", evaluateCodingSubmission);
});

const appendAssistantMessage = (sender, text) => {
  if (!assistantThread) return;

  const message = document.createElement("article");
  const meta = document.createElement("span");
  const body = document.createElement("p");

  message.className = `assistant-message ${sender}`;
  meta.textContent = sender === "student" ? "林同学 · 刚刚" : "Python 小助手 · 刚刚";
  body.textContent = text;
  message.append(meta, body);
  assistantThread.append(message);
  assistantThread.scrollTop = assistantThread.scrollHeight;
};

assistantSend?.addEventListener("click", () => {
  const text = assistantInput?.value.trim();
  if (!text) return;

  appendAssistantMessage("student", text);
  assistantInput.value = "";
  appendAssistantMessage(
    "ai",
    "我们沿着你的想法继续：你能用一个具体测试用例说明 left 为什么不能回退吗？比如 abba 中第二个 a 出现时，当前窗口是什么？",
  );
});

assistantInput?.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
    assistantSend?.click();
  }
});

policySave?.addEventListener("click", () => {
  if (!policyStatus) return;

  policyStatus.textContent = "已保存：学生端小助手将使用当前苏格拉底式提示规范。";
  policyStatus.classList.add("is-done");
});

knowledgeNodes.forEach((node) => {
  node.addEventListener("click", () => {
    knowledgeNodes.forEach((item) => item.classList.remove("active"));
    node.classList.add("active");
  });
});

studentSelectors.forEach((selector) => {
  selector.addEventListener("click", () => {
    studentSelectors.forEach((item) => item.classList.remove("active"));
    selector.classList.add("active");
  });
});

domainSave?.addEventListener("click", () => {
  if (!domainStatus) return;

  domainStatus.textContent = "已保存：Q 矩阵、诊断规则和模型参数已同步到教学推荐流程。";
  domainStatus.classList.add("is-done");
});

weightSliders.forEach((slider) => {
  slider.addEventListener("input", () => {
    const valueLabel = slider.nextElementSibling;
    if (valueLabel) {
      valueLabel.textContent = `${slider.value}%`;
    }
  });
});

teachingSave?.addEventListener("click", () => {
  if (!teachingStatus) return;

  teachingStatus.textContent = "已保存：新的推荐策略将用于下一题推荐、补救路径和复习调度。";
  teachingStatus.classList.add("is-done");
});

roleCards.forEach((card) => {
  card.addEventListener("click", () => {
    selectedRole = card.dataset.role;
    updateLoginView(selectedRole);
    showAuthView("login");
    renderIcons();
  });
});

authBack?.addEventListener("click", () => {
  showAuthView("role");
  renderIcons();
});

loginForm?.addEventListener("submit", (event) => {
  event.preventDefault();
  enterWorkspace(selectedRole);
});

logoutButton?.addEventListener("click", resetWorkspace);

const appendMessage = () => {
  const text = chatInput.value.trim();

  if (!text || !chatPanel) return;

  const message = document.createElement("article");
  const meta = document.createElement("span");
  const body = document.createElement("p");

  message.className = "message user";
  meta.textContent = `${roleCopy[selectedRole]?.userName ?? "林老师"} · 刚刚`;
  body.textContent = text;
  message.append(meta, body);
  chatPanel.insertBefore(message, chatPanel.querySelector(".composer"));
  chatInput.value = "";
};

chatButton?.addEventListener("click", appendMessage);

chatInput?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    appendMessage();
  }
});

window.addEventListener("load", renderIcons);
