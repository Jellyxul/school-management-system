/**
 * 公共 JS：统一请求封装、消息提示、确认框、分页渲染
 * 后端统一响应格式：{code: 0, msg: "success", data: ...}，业务失败时 HTTP 200 + code 非 0
 */

/**
 * 统一请求封装：解析统一响应体，code !== 0 时提示错误并 reject，成功返回 data
 */
async function api(path, { method = "GET", body = null } = {}) {
    let resp;
    try {
        resp = await fetch(path, {
            method: method,
            headers: body ? { "Content-Type": "application/json" } : undefined,
            body: body ? JSON.stringify(body) : null,
        });
    } catch (e) {
        showToast("网络请求失败，请确认后端服务已启动", "danger");
        throw e;
    }
    let result;
    try {
        result = await resp.json();
    } catch (e) {
        showToast("服务异常（HTTP " + resp.status + "）", "danger");
        throw e;
    }
    if (result.code !== 0) {
        showToast(result.msg || "操作失败", "danger");
        throw new Error(result.msg || "操作失败");
    }
    return result.data;
}

/** 轻提示：页面顶部居中弹出，3 秒后自动消失 */
function showToast(msg, type) {
    type = type || "success";
    let box = document.getElementById("toastBox");
    if (!box) {
        box = document.createElement("div");
        box.id = "toastBox";
        box.style.cssText = "position:fixed;top:16px;left:50%;transform:translateX(-50%);z-index:2000;";
        document.body.appendChild(box);
    }
    const div = document.createElement("div");
    div.className = "alert alert-" + type + " py-2 px-3 shadow-sm mb-2";
    div.setAttribute("role", "alert");
    div.textContent = msg;
    box.appendChild(div);
    setTimeout(function () { div.remove(); }, 3000);
}

/** 确认框：返回 Promise<boolean>，确定返回 true、取消返回 false */
function confirmDialog(msg) {
    msg = msg || "确定执行该操作吗？";
    return new Promise(function (resolve) {
        const id = "dynConfirmModal" + Date.now();
        document.body.insertAdjacentHTML("beforeend",
            '<div class="modal fade" id="' + id + '" tabindex="-1">' +
            '  <div class="modal-dialog modal-sm modal-dialog-centered">' +
            '    <div class="modal-content">' +
            '      <div class="modal-header py-2"><h6 class="modal-title">提示</h6>' +
            '        <button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>' +
            '      <div class="modal-body py-3">' + msg + '</div>' +
            '      <div class="modal-footer py-2">' +
            '        <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">取消</button>' +
            '        <button type="button" class="btn btn-primary btn-sm" data-ok>确定</button>' +
            '      </div>' +
            '    </div>' +
            '  </div>' +
            '</div>');
        const el = document.getElementById(id);
        const modal = new bootstrap.Modal(el);
        el.querySelector("[data-ok]").addEventListener("click", function () {
            resolve(true);
            modal.hide();
        });
        el.addEventListener("hidden.bs.modal", function () {
            el.remove();
            resolve(false);
        }, { once: true });
        modal.show();
    });
}

/**
 * 渲染分页条
 * @param el     ul.pagination 容器
 * @param total  总条数
 * @param page   当前页
 * @param size   每页条数
 * @param onPage 页码变更回调 function(newPage)
 */
function renderPagination(el, total, page, size, onPage) {
    const totalPages = Math.max(1, Math.ceil(total / size));
    el.innerHTML = "";
    const add = function (label, target, opts) {
        opts = opts || {};
        const li = document.createElement("li");
        li.className = "page-item" + (opts.disabled ? " disabled" : "") + (opts.active ? " active" : "");
        const a = document.createElement("a");
        a.className = "page-link";
        a.href = "javascript:;";
        a.textContent = label;
        if (!opts.disabled && !opts.active) {
            a.addEventListener("click", function () { onPage(target); });
        }
        li.appendChild(a);
        el.appendChild(li);
    };
    add("上一页", page - 1, { disabled: page <= 1 });
    let start = Math.max(1, page - 2);
    let end = Math.min(totalPages, start + 4);
    start = Math.max(1, end - 4);
    for (let p = start; p <= end; p++) {
        add(String(p), p, { active: p === page });
    }
    add("下一页", page + 1, { disabled: page >= totalPages });
}

/** 日期显示格式化：去掉 T、截到秒 */
function formatDate(v) {
    if (!v) return "-";
    return String(v).replace("T", " ").slice(0, 19);
}

/** 返回首页：模块页在首页框架 iframe 中时，触发父页面「首页」菜单；独立打开时直接跳转框架页 */
function goHome() {
    try {
        if (window.parent && window.parent !== window) {
            const homeLink = window.parent.document.querySelector('.sidebar-menu a[data-page=""]');
            if (homeLink) {
                homeLink.click();
                return;
            }
        }
    } catch (e) { /* 异常时走直接跳转 */ }
    window.top.location.href = "/static/html/index.html";
}

/**
 * 自定义下拉组件：把带 js-dd 类的原生 select 包装成打开时有渐进动效的下拉
 * 原生 select 保留并隐藏，表单取值、reset 逻辑不变；菜单打开时按当前选项即时渲染，
 * 因此选项动态变化（如异步加载教师列表）无需刷新组件
 */
function initDropdowns(root) {
    (root || document).querySelectorAll("select.js-dd").forEach(function (sel) {
        if (sel.dataset.ddInit) return;
        sel.dataset.ddInit = "1";
        sel.setAttribute("hidden", "");

        // 包一层容器：隐藏的原生 select + 触发按钮 + 动画菜单
        const wrap = document.createElement("div");
        wrap.className = "sel-dd";
        sel.parentNode.insertBefore(wrap, sel);
        wrap.appendChild(sel);

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "form-select form-select-sm sel-dd-btn";
        wrap.appendChild(btn);

        const menu = document.createElement("ul");
        menu.className = "sel-dd-menu list-unstyled mb-0";
        wrap.appendChild(menu);

        function close() { menu.classList.remove("open"); }

        function renderMenu() {
            menu.innerHTML = "";
            Array.prototype.forEach.call(sel.options, function (opt) {
                const li = document.createElement("li");
                li.textContent = opt.text;
                li.dataset.value = opt.value;
                if (opt.value === sel.value) li.classList.add("selected");
                li.addEventListener("click", function () {
                    sel.value = opt.value;
                    syncDropdownLabel(sel);
                    close();
                });
                menu.appendChild(li);
            });
            if (!menu.children.length) {
                const li = document.createElement("li");
                li.className = "text-muted";
                li.textContent = "暂无选项";
                menu.appendChild(li);
            }
        }

        btn.addEventListener("click", function (e) {
            e.stopPropagation();
            const willOpen = !menu.classList.contains("open");
            closeAllDropdowns();
            if (willOpen) {
                renderMenu();
                menu.classList.add("open");
            }
        });
        menu.addEventListener("click", function (e) { e.stopPropagation(); });

        syncDropdownLabel(sel);
    });
}

/** 关闭页面上所有打开的下拉（点击外部收起） */
function closeAllDropdowns() {
    document.querySelectorAll(".sel-dd-menu.open").forEach(function (m) {
        m.classList.remove("open");
    });
}

/** 程序修改 select 值后，同步下拉按钮的显示文字 */
function syncDropdownLabel(sel) {
    if (!sel || !sel.parentNode) return;
    const btn = sel.parentNode.querySelector(".sel-dd-btn");
    if (!btn) return;
    btn.textContent = sel.selectedIndex >= 0 ? sel.options[sel.selectedIndex].text : "请选择";
}

/** 同步表单内全部自定义下拉的按钮显示（reset / 回填后调用） */
function syncFormDropdowns(form) {
    form.querySelectorAll("select.js-dd").forEach(syncDropdownLabel);
}

// 页面脚本在 body 末尾加载，DOM 就绪，直接初始化
initDropdowns();
document.addEventListener("click", closeAllDropdowns);

/**
 * 通知公告（纯前端模拟）公共存储：通知公告页与首页"最新公告"卡片共用
 * 数据存 localStorage；首次访问时写入静态模拟数据，之后增删改查均直接更新
 */
const NOTICE_KEY = "noticeList";

const NOTICE_SEED = [
    { id: 3, title: "系统维护通知", content: "系统将于本周六 22:00 至次日 6:00 进行例行维护，期间服务可能短暂不可用，请提前保存数据。", publisher: "管理员", publish_time: "2026-10-21 09:00:00" },
    { id: 2, title: "关于期中考试安排的通知", content: "本学期期中考试定于第 9 周周三至周五举行，请各位同学提前复习，按时参加考试。", publisher: "教务处", publish_time: "2026-10-19 14:30:00" },
    { id: 1, title: "欢迎使用新管理系统", content: "新版管理系统上线，支持学生、教师、课程、班级、排课、选课与成绩的一站式管理。", publisher: "Admin", publish_time: "2026-10-15 08:00:00" },
];

/** 读取公告列表；首次访问写入静态模拟数据 */
function loadNotices() {
    const raw = localStorage.getItem(NOTICE_KEY);
    if (raw === null) {
        saveNotices(NOTICE_SEED.slice());
        return NOTICE_SEED.slice();
    }
    try {
        return JSON.parse(raw) || [];
    } catch (e) {
        return [];
    }
}

/** 保存公告列表 */
function saveNotices(list) {
    localStorage.setItem(NOTICE_KEY, JSON.stringify(list));
}

/** 当前时间文本，如 2026-10-21 15:30:00 */
function noticeNowText() {
    const d = new Date();
    const p = function (n) { return String(n).padStart(2, "0"); };
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) +
        " " + p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds());
}
