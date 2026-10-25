/**
 * 班级管理页面逻辑
 * 接口：GET /clazz/page、GET /clazz/{id}、POST /clazz/add、
 *       PUT /clazz/update/{id}、DELETE /clazz/delete/{id}
 */
const clazzState = { page: 1, size: 10, keyword: "" };
const clazzTableBody = document.getElementById("tableBody");

/** 加载班级分页数据并渲染 */
async function loadClazzTable() {
    const params = new URLSearchParams({
        page: clazzState.page, size: clazzState.size, keyword: clazzState.keyword,
    });
    try {
        const data = await api("/clazz/page?" + params.toString());
        renderClazzRows(data.rows || []);
        document.getElementById("totalInfo").textContent = "共 " + data.total + " 条";
        renderPagination(document.getElementById("pagination"), data.total, data.page, data.size,
            function (p) { clazzState.page = p; loadClazzTable(); });
    } catch (e) {
        clazzTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">暂无数据</td></tr>';
    }
}

function renderClazzRows(rows) {
    if (!rows.length) {
        clazzTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">暂无数据</td></tr>';
        return;
    }
    clazzTableBody.innerHTML = rows.map(function (r) {
        return '<tr>' +
            '<td>' + r.id + '</td>' +
            '<td>' + r.name + '</td>' +
            '<td>' + r.code + '</td>' +
            '<td>' + r.teacher_id + '</td>' +
            '<td>' + (r.address || "-") + '</td>' +
            '<td>' + formatDate(r.create_time) + '</td>' +
            '<td>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openClazzEdit(' + r.id + ')">修改</button>' +
            '  <button class="btn btn-link btn-sm p-0 text-danger" onclick="removeClazz(' + r.id + ')">删除</button>' +
            '</td>' +
            '</tr>';
    }).join("");
}

/** 加载班主任下拉选项（全部已有教师），并同步下拉按钮显示 */
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
async function openClazzAdd() {
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["cid"].value = "";
    try {
        await loadTeacherOptions();
    } catch (e) {
        return; /* api 已提示加载失败 */
    }
    syncFormDropdowns(form);
    document.getElementById("editTitle").textContent = "新增班级";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 打开修改弹窗：先查详情回填 */
async function openClazzEdit(id) {
    try {
        const clazz = await api("/clazz/" + id);
        try {
            await loadTeacherOptions();
        } catch (e) {
            return; /* api 已提示加载失败 */
        }
        const form = document.getElementById("editForm");
        form.reset();
        form.elements["cid"].value = clazz.id;
        form.elements["name"].value = clazz.name;
        form.elements["code"].value = clazz.code;
        form.elements["teacher_id"].value = clazz.teacher_id;
        form.elements["address"].value = clazz.address || "";
        syncFormDropdowns(form);
        document.getElementById("editTitle").textContent = "修改班级";
        bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
    } catch (e) { /* api 已提示 */ }
}

/** 提交新增/修改 */
document.getElementById("editForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const f = e.target;
    const id = f.elements["cid"].value;
    const payload = {
        name: f.elements["name"].value.trim(),
        code: f.elements["code"].value.trim(),
        teacher_id: parseInt(f.elements["teacher_id"].value, 10),
        address: f.elements["address"].value.trim() || null,
    };
    try {
        if (id) {
            await api("/clazz/update/" + id, { method: "PUT", body: payload });
        } else {
            await api("/clazz/add", { method: "POST", body: payload });
        }
        bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
        showToast(id ? "修改成功" : "新增成功");
        loadClazzTable();
    } catch (e) { /* api 已提示 */ }
});

/** 删除班级 */
async function removeClazz(id) {
    const yes = await confirmDialog("确定删除 ID 为 " + id + " 的班级吗？");
    if (!yes) return;
    try {
        await api("/clazz/delete/" + id, { method: "DELETE" });
        showToast("删除成功");
        loadClazzTable();
    } catch (e) { /* api 已提示 */ }
}

/** 搜索 */
document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    clazzState.keyword = document.getElementById("keyword").value.trim();
    clazzState.page = 1;
    loadClazzTable();
});

/** 重置 */
document.getElementById("btnReset").addEventListener("click", function () {
    document.getElementById("keyword").value = "";
    clazzState.keyword = "";
    clazzState.page = 1;
    loadClazzTable();
});

document.getElementById("btnAdd").addEventListener("click", openClazzAdd);

loadClazzTable();
