/**
 * 课程管理页面逻辑
 * 接口：GET /subject/page、GET /subject/{id}、POST /subject/add、
 *       PUT /subject/update/{id}、DELETE /subject/delete/{id}
 */
const subState = { page: 1, size: 10, keyword: "" };
const subTableBody = document.getElementById("tableBody");

/** 加载课程分页数据并渲染 */
async function loadSubjectTable() {
    const params = new URLSearchParams({
        page: subState.page, size: subState.size, keyword: subState.keyword,
    });
    try {
        const data = await api("/subject/page?" + params.toString());
        renderSubjectRows(data.rows || []);
        document.getElementById("totalInfo").textContent = "共 " + data.total + " 条";
        renderPagination(document.getElementById("pagination"), data.total, data.page, data.size,
            function (p) { subState.page = p; loadSubjectTable(); });
    } catch (e) {
        subTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-3">暂无数据</td></tr>';
    }
}

function renderSubjectRows(rows) {
    if (!rows.length) {
        subTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-3">暂无数据</td></tr>';
        return;
    }
    subTableBody.innerHTML = rows.map(function (r) {
        return '<tr>' +
            '<td>' + r.id + '</td>' +
            '<td>' + r.name + '</td>' +
            '<td>' + r.credit + '</td>' +
            '<td>' + r.teacher_id + '</td>' +
            '<td>' + formatDate(r.create_time) + '</td>' +
            '<td>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openSubjectEdit(' + r.id + ')">修改</button>' +
            '  <button class="btn btn-link btn-sm p-0 text-danger" onclick="removeSubject(' + r.id + ')">删除</button>' +
            '</td>' +
            '</tr>';
    }).join("");
}

/** 加载授课教师下拉选项（全部已有教师），并同步下拉按钮显示 */
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
async function openSubjectAdd() {
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["subid"].value = "";
    try {
        await loadTeacherOptions();
    } catch (e) {
        return; /* api 已提示加载失败 */
    }
    syncFormDropdowns(form);
    document.getElementById("editTitle").textContent = "新增课程";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 打开修改弹窗：先查详情回填 */
async function openSubjectEdit(id) {
    try {
        const sub = await api("/subject/" + id);
        try {
            await loadTeacherOptions();
        } catch (e) {
            return; /* api 已提示加载失败 */
        }
        const form = document.getElementById("editForm");
        form.reset();
        form.elements["subid"].value = sub.id;
        form.elements["name"].value = sub.name;
        form.elements["credit"].value = sub.credit;
        form.elements["teacher_id"].value = sub.teacher_id;
        syncFormDropdowns(form);
        document.getElementById("editTitle").textContent = "修改课程";
        bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
    } catch (e) { /* api 已提示 */ }
}

/** 提交新增/修改 */
document.getElementById("editForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const f = e.target;
    const id = f.elements["subid"].value;
    const credit = f.elements["credit"].value;
    const payload = {
        name: f.elements["name"].value.trim(),
        credit: credit === "" ? 0 : parseInt(credit, 10),   // 学分缺省按 0 提交
        teacher_id: parseInt(f.elements["teacher_id"].value, 10),
    };
    try {
        if (id) {
            await api("/subject/update/" + id, { method: "PUT", body: payload });
        } else {
            await api("/subject/add", { method: "POST", body: payload });
        }
        bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
        showToast(id ? "修改成功" : "新增成功");
        loadSubjectTable();
    } catch (e) { /* api 已提示 */ }
});

/** 删除课程 */
async function removeSubject(id) {
    const yes = await confirmDialog("确定删除 ID 为 " + id + " 的课程吗？");
    if (!yes) return;
    try {
        await api("/subject/delete/" + id, { method: "DELETE" });
        showToast("删除成功");
        loadSubjectTable();
    } catch (e) { /* api 已提示 */ }
}

/** 搜索 */
document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    subState.keyword = document.getElementById("keyword").value.trim();
    subState.page = 1;
    loadSubjectTable();
});

/** 重置 */
document.getElementById("btnReset").addEventListener("click", function () {
    document.getElementById("keyword").value = "";
    subState.keyword = "";
    subState.page = 1;
    loadSubjectTable();
});

document.getElementById("btnAdd").addEventListener("click", openSubjectAdd);

loadSubjectTable();
