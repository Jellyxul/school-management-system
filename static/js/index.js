/**
 * 首页框架逻辑：侧边栏菜单切换 iframe 内容区、面包屑联动
 */
(function () {
    const frame = document.getElementById("contentFrame");
    const welcome = document.getElementById("welcome");
    const breadcrumb = document.getElementById("breadcrumb");
    const links = document.querySelectorAll("[data-page]");

    links.forEach(function (link) {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            // 高亮侧边栏菜单
            document.querySelectorAll(".sidebar-menu a").forEach(function (l) { l.classList.remove("active"); });
            const menuLink = document.querySelector('.sidebar-menu a[data-page="' + link.dataset.page + '"]');
            if (menuLink) {
                menuLink.classList.add("active");
                // 高亮项在折叠分组内时自动展开该分组
                const sub = menuLink.closest(".submenu");
                if (sub && !sub.classList.contains("show")) {
                    bootstrap.Collapse.getOrCreateInstance(sub).show();
                }
            }

            const page = link.dataset.page;
            const title = link.dataset.title;
            breadcrumb.textContent = title === "首页" ? "首页" : "首页 / " + title;

            if (!page) {
                // 首页：显示欢迎面板
                welcome.style.display = "block";
                frame.style.display = "none";
                frame.src = "about:blank";
                renderDashboard();
                return;
            }
            welcome.style.display = "none";
            frame.style.display = "block";
            frame.src = "/static/html/" + page;
        });
    });

    // 分组折叠：箭头随展开状态旋转（监听 Bootstrap Collapse 事件）
    document.querySelectorAll(".menu-group").forEach(function (group) {
        const panel = group.querySelector(".collapse");
        if (!panel) return;
        panel.addEventListener("show.bs.collapse", function () { group.classList.add("open"); });
        panel.addEventListener("hide.bs.collapse", function () { group.classList.remove("open"); });
    });

    /** 渲染首页"最新公告"卡片（与通知公告页共用 localStorage 数据） */
    function renderLatestNotices() {
        const el = document.getElementById("latestNoticeList");
        if (!el) return;
        const list = loadNotices()
            .sort(function (a, b) { return b.publish_time.localeCompare(a.publish_time); })
            .slice(0, 3);
        el.innerHTML = list.length
            ? list.map(function (n) {
                return '<li class="list-group-item d-flex justify-content-between align-items-center py-2">' +
                    '<span class="text-truncate me-2">📢 ' + n.title + '</span>' +
                    '<small class="text-muted text-nowrap">' + n.publish_time.slice(0, 10) + '</small>' +
                    '</li>';
            }).join("")
            : '<li class="list-group-item text-muted text-center py-3">暂无公告</li>';
    }

    /** 加载看板统计：学生/教师/课程/班级总数（后端聚合接口 /dashboard/stats） */
    async function loadDashboardStats() {
        const map = [
            ["statStudent", "student_count"],
            ["statTeacher", "teacher_count"],
            ["statSubject", "subject_count"],
            ["statClazz", "clazz_count"],
        ];
        try {
            const stats = await api("/dashboard/stats");
            map.forEach(function (pair) {
                const el = document.getElementById(pair[0]);
                if (el) el.textContent = stats[pair[1]] || 0;
            });
        } catch (e) {
            map.forEach(function (pair) {
                const el = document.getElementById(pair[0]);
                if (el) el.textContent = "-";
            });
        }
    }

    /** 加载今日排课：取排课列表，按上课时间中的星期匹配今天 */
    async function loadTodayArrangements() {
        const el = document.getElementById("todayList");
        if (!el) return;
        const label = document.getElementById("todayLabel");
        const weekdays = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];
        const d = new Date();
        const today = weekdays[d.getDay()];
        const p = function (n) { return String(n).padStart(2, "0"); };
        if (label) {
            label.textContent = d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) + " " + today;
        }
        let rows;
        try {
            rows = await api("/arrangement/list");
        } catch (e) {
            el.innerHTML = '<li class="list-group-item text-muted text-center py-4">加载失败，请确认后端服务已启动</li>';
            return;
        }
        // class_time 形如 "周一 1-2节"，按今天星期过滤
        const list = (rows || []).filter(function (r) {
            return r.class_time && r.class_time.indexOf(today) !== -1;
        });
        if (!list.length) {
            el.innerHTML = '<li class="list-group-item text-muted text-center py-4">今日暂无排课</li>';
            return;
        }
        el.innerHTML = list.map(function (r) {
            return '<li class="list-group-item d-flex justify-content-between align-items-center py-2">' +
                '<div><span class="fw-bold">' + r.course_name + '</span>' +
                '<span class="text-muted small ms-2">' + r.teacher_name + '</span></div>' +
                '<div class="text-nowrap text-muted small">' + r.class_time + ' · ' + r.classroom + '</div>' +
                '</li>';
        }).join("");
    }

    /** 加载/刷新首页看板（首次进入与每次点回首页时调用） */
    function renderDashboard() {
        loadDashboardStats();
        loadTodayArrangements();
        renderLatestNotices();
    }

    renderDashboard();
})();
