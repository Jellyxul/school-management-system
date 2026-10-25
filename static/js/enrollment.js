/**
 * 选课与成绩管理页面逻辑
 * 接口：GET /enrollment/page、GET /enrollment/{id}、POST /enrollment/add、
 *       PUT /enrollment/update/{id}（基础信息）、PUT /enrollment/score/{id}（仅成绩与状态）、
 *       DELETE /enrollment/delete/{id}
 */
const enrState = { page: 1, size: 10, keyword: "" };
const enrTableBody = document.getElementById("tableBody");

/** 加载选课分页数据并渲染（列表已带出学生姓名与课程名称） */
async function loadEnrollmentTable() {
    const params = new URLSearchParams({
        page: enrState.page, size: enrState.size, keyword: enrState.keyword,
    });
    try {
        const data = await api("/enrollment/page?" + params.toString());
        renderEnrollmentRows(data.rows || []);
        document.getElementById("totalInfo").textContent = "共 " + data.total + " 条";
        renderPagination(document.getElementById("pagination"), data.total, data.page, data.size,
            function (p) { enrState.page = p; loadEnrollmentTable(); });
    } catch (e) {
        enrTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-3">暂无数据</td></tr>';
    }
}

function renderEnrollmentRows(rows) {
    if (!rows.length) {
        enrTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-3">暂无数据</td></tr>';
        return;
    }
    enrTableBody.innerHTML = rows.map(function (r) {
        return '<tr>' +
            '<td>' + r.id + '</td>' +
            '<td>' + (r.student_name || r.student_id) + '</td>' +
            '<td>' + (r.course_name || r.course_id) + '</td>' +
            '<td>' + r.term + '</td>' +
            '<td>' + (r.score === null || r.score === undefined ? "-" : r.score) + '</td>' +
            '<td>' + r.status + '</td>' +
            '<td>' + formatDate(r.create_time) + '</td>' +
            '<td>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openEnrollmentEdit(' + r.id + ')">修改</button>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openScoreEdit(' + r.id + ')">录入成绩</button>' +
            '  <button class="btn btn-link btn-sm p-0 text-danger" onclick="removeEnrollment(' + r.id + ')">删除</button>' +
            '</td>' +
            '</tr>';
    }).join("");
}

/** 加载学生下拉选项（全部已有学生），并同步下拉按钮显示 */
async function loadStudentOptions() {
    const list = await api("/student/list");
    const select = document.getElementById("studentSelect");
    const current = select.value;
    select.innerHTML = (list || []).map(function (s) {
        return '<option value="' + s.id + '">' + s.id + ' - ' + s.name + '</option>';
    }).join("");
    // 保留之前已选中的学生（如有）
    if (current && select.querySelector('option[value="' + current + '"]')) {
        select.value = current;
    }
    syncDropdownLabel(select);
}

/** 加载课程下拉选项（全部已有课程），并同步下拉按钮显示 */
async function loadCourseOptions() {
    const list = await api("/subject/list");
    const select = document.getElementById("courseSelect");
    const current = select.value;
    select.innerHTML = (list || []).map(function (c) {
        return '<option value="' + c.id + '">' + c.id + ' - ' + c.name + '</option>';
    }).join("");
    // 保留之前已选中的课程（如有）
    if (current && select.querySelector('option[value="' + current + '"]')) {
        select.value = current;
    }
    syncDropdownLabel(select);
}

/** 打开新增弹窗 */
async function openEnrollmentAdd() {
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["eid"].value = "";
    try {
        await loadStudentOptions();
        await loadCourseOptions();
    } catch (e) {
        return; /* api 已提示加载失败 */
    }
    syncFormDropdowns(form);
    document.getElementById("editTitle").textContent = "新增选课";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 打开修改弹窗（基础信息，不含成绩）：先查详情回填 */
async function openEnrollmentEdit(id) {
    try {
        const enr = await api("/enrollment/" + id);
        try {
            await loadStudentOptions();
            await loadCourseOptions();
        } catch (e) {
            return; /* api 已提示加载失败 */
        }
        const form = document.getElementById("editForm");
        form.reset();
        form.elements["eid"].value = enr.id;
        form.elements["student_id"].value = enr.student_id;
        form.elements["course_id"].value = enr.course_id;
        form.elements["term"].value = enr.term;
        form.elements["status"].value = enr.status;
        syncFormDropdowns(form);
        document.getElementById("editTitle").textContent = "修改选课";
        bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
    } catch (e) { /* api 已提示 */ }
}

/** 打开录入成绩弹窗（仅成绩与状态） */
async function openScoreEdit(id) {
    try {
        const enr = await api("/enrollment/" + id);
        const form = document.getElementById("scoreForm");
        form.reset();
        form.elements["seid"].value = enr.id;
        form.elements["score"].value = (enr.score === null || enr.score === undefined) ? "" : enr.score;
        form.elements["status"].value = enr.status;
        syncFormDropdowns(form);
        document.getElementById("scoreTitle").textContent =
            "录入成绩：" + enr.student_name + " - " + enr.course_name;
        bootstrap.Modal.getOrCreateInstance(document.getElementById("scoreModal")).show();
    } catch (e) { /* api 已提示 */ }
}

/** 提交新增/修改（基础信息） */
document.getElementById("editForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const f = e.target;
    const id = f.elements["eid"].value;
    const term = f.elements["term"].value.trim();
    const payload = {
        student_id: parseInt(f.elements["student_id"].value, 10),
        course_id: parseInt(f.elements["course_id"].value, 10),
        term: term || null,   // 不填由服务端默认当前学期
        status: f.elements["status"].value,
    };
    try {
        if (id) {
            await api("/enrollment/update/" + id, { method: "PUT", body: payload });
        } else {
            await api("/enrollment/add", { method: "POST", body: payload });
        }
        bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
        showToast(id ? "修改成功" : "新增成功");
        loadEnrollmentTable();
    } catch (e) { /* api 已提示 */ }
});

/** 提交录入成绩（仅成绩与状态） */
document.getElementById("scoreForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const f = e.target;
    const id = f.elements["seid"].value;
    const score = f.elements["score"].value;
    const payload = {
        score: score === "" ? null : parseInt(score, 10),   // 留空表示未录入（清空成绩）
        status: f.elements["status"].value,
    };
    try {
        await api("/enrollment/score/" + id, { method: "PUT", body: payload });
        bootstrap.Modal.getInstance(document.getElementById("scoreModal")).hide();
        showToast("成绩录入成功");
        loadEnrollmentTable();
    } catch (e) { /* api 已提示 */ }
});

/** 删除选课记录 */
async function removeEnrollment(id) {
    const yes = await confirmDialog("确定删除 ID 为 " + id + " 的选课记录吗？");
    if (!yes) return;
    try {
        await api("/enrollment/delete/" + id, { method: "DELETE" });
        showToast("删除成功");
        loadEnrollmentTable();
    } catch (e) { /* api 已提示 */ }
}

/** 搜索 */
document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    enrState.keyword = document.getElementById("keyword").value.trim();
    enrState.page = 1;
    loadEnrollmentTable();
});

/** 重置 */
document.getElementById("btnReset").addEventListener("click", function () {
    document.getElementById("keyword").value = "";
    enrState.keyword = "";
    enrState.page = 1;
    loadEnrollmentTable();
});

document.getElementById("btnAdd").addEventListener("click", openEnrollmentAdd);

loadEnrollmentTable();
