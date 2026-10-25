/**
 * 排课管理页面逻辑
 * 接口：GET /arrangement/page、GET /arrangement/{id}、POST /arrangement/add、
 *       PUT /arrangement/update/{id}、DELETE /arrangement/delete/{id}
 */
const arrState = { page: 1, size: 10, keyword: "" };
const arrTableBody = document.getElementById("tableBody");

/** 加载排课分页数据并渲染（列表已带出课程名称与教师名称） */
async function loadArrangementTable() {
    const params = new URLSearchParams({
        page: arrState.page, size: arrState.size, keyword: arrState.keyword,
    });
    try {
        const data = await api("/arrangement/page?" + params.toString());
        renderArrangementRows(data.rows || []);
        document.getElementById("totalInfo").textContent = "共 " + data.total + " 条";
        renderPagination(document.getElementById("pagination"), data.total, data.page, data.size,
            function (p) { arrState.page = p; loadArrangementTable(); });
    } catch (e) {
        arrTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-3">暂无数据</td></tr>';
    }
}

function renderArrangementRows(rows) {
    if (!rows.length) {
        arrTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-3">暂无数据</td></tr>';
        return;
    }
    arrTableBody.innerHTML = rows.map(function (r) {
        return '<tr>' +
            '<td>' + r.id + '</td>' +
            '<td>' + (r.course_name || r.course_id) + '</td>' +
            '<td>' + (r.teacher_name || r.teacher_id) + '</td>' +
            '<td>' + r.term + '</td>' +
            '<td>' + r.classroom + '</td>' +
            '<td>' + r.class_time + '</td>' +
            '<td>' + formatDate(r.create_time) + '</td>' +
            '<td>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openArrangementEdit(' + r.id + ')">修改</button>' +
            '  <button class="btn btn-link btn-sm p-0 text-danger" onclick="removeArrangement(' + r.id + ')">删除</button>' +
            '</td>' +
            '</tr>';
    }).join("");
}

/** 加载课程下拉选项（全部已有课程），并同步下拉按钮显示 */
async function loadCourseOptions() {
    const list = await api("/subject/list");
    const select = document.getElementById("courseSelect");
    const current = select.value;
    select.innerHTML = (list || []).map(function (s) {
        return '<option value="' + s.id + '">' + s.id + ' - ' + s.name + '</option>';
    }).join("");
    // 保留之前已选中的课程（如有）
    if (current && select.querySelector('option[value="' + current + '"]')) {
        select.value = current;
    }
    syncDropdownLabel(select);
}

/** 加载教师下拉选项（全部已有教师），并同步下拉按钮显示 */
async function loadTeacherOptions() {
    const list = await api("/teacher/list");
    const select = document.getElementById("teacherSelect");
    const current = select.value;
    select.innerHTML = (list || []).map(function (t) {
        return '<option value="' + t.id + '">' + t.id + ' - ' + t.name + '</option>';
    }).join("");
    // 保留之前已选中的教师（如有）
    if (current && select.querySelector('option[value="' + current + '"]')) {
        select.value = current;
    }
    syncDropdownLabel(select);
}

/** 打开新增弹窗 */
async function openArrangementAdd() {
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["aid"].value = "";
    try {
        await loadCourseOptions();
        await loadTeacherOptions();
    } catch (e) {
        return; /* api 已提示加载失败 */
    }
    syncFormDropdowns(form);
    document.getElementById("editTitle").textContent = "新增排课";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 打开修改弹窗：先查详情回填 */
async function openArrangementEdit(id) {
    try {
        const arr = await api("/arrangement/" + id);
        try {
            await loadCourseOptions();
            await loadTeacherOptions();
        } catch (e) {
            return; /* api 已提示加载失败 */
        }
        const form = document.getElementById("editForm");
        form.reset();
        form.elements["aid"].value = arr.id;
        form.elements["course_id"].value = arr.course_id;
        form.elements["teacher_id"].value = arr.teacher_id;
        form.elements["term"].value = arr.term;
        form.elements["classroom"].value = arr.classroom;
        form.elements["class_time"].value = arr.class_time;
        syncFormDropdowns(form);
        document.getElementById("editTitle").textContent = "修改排课";
        bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
    } catch (e) { /* api 已提示 */ }
}

/** 提交新增/修改 */
document.getElementById("editForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const f = e.target;
    const id = f.elements["aid"].value;
    const term = f.elements["term"].value.trim();
    const payload = {
        course_id: parseInt(f.elements["course_id"].value, 10),
        teacher_id: parseInt(f.elements["teacher_id"].value, 10),
        term: term || null,   // 不填由服务端默认当前学期
        classroom: f.elements["classroom"].value.trim(),
        class_time: f.elements["class_time"].value.trim(),
    };
    try {
        if (id) {
            await api("/arrangement/update/" + id, { method: "PUT", body: payload });
        } else {
            await api("/arrangement/add", { method: "POST", body: payload });
        }
        bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
        showToast(id ? "修改成功" : "新增成功");
        loadArrangementTable();
    } catch (e) { /* api 已提示 */ }
});

/** 删除排课 */
async function removeArrangement(id) {
    const yes = await confirmDialog("确定删除 ID 为 " + id + " 的排课吗？");
    if (!yes) return;
    try {
        await api("/arrangement/delete/" + id, { method: "DELETE" });
        showToast("删除成功");
        loadArrangementTable();
    } catch (e) { /* api 已提示 */ }
}

/** 搜索 */
document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    arrState.keyword = document.getElementById("keyword").value.trim();
    arrState.page = 1;
    loadArrangementTable();
});

/** 重置 */
document.getElementById("btnReset").addEventListener("click", function () {
    document.getElementById("keyword").value = "";
    arrState.keyword = "";
    arrState.page = 1;
    loadArrangementTable();
});

document.getElementById("btnAdd").addEventListener("click", openArrangementAdd);

loadArrangementTable();
