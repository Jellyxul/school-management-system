/**
 * 学生管理页面逻辑
 * 接口：GET /student/page、GET /student/{id}、POST /student/add、
 *       PUT /student/update/{id}、DELETE /student/delete/{id}
 */
const GENDER_TEXT = { man: "男", woman: "女" };

const stuState = { page: 1, size: 10, keyword: "" };
const stuTableBody = document.getElementById("tableBody");

/** 加载学生分页数据并渲染 */
async function loadStudentTable() {
    const params = new URLSearchParams({
        page: stuState.page, size: stuState.size, keyword: stuState.keyword,
    });
    try {
        const data = await api("/student/page?" + params.toString());
        renderStudentRows(data.rows || []);
        document.getElementById("totalInfo").textContent = "共 " + data.total + " 条";
        renderPagination(document.getElementById("pagination"), data.total, data.page, data.size,
            function (p) { stuState.page = p; loadStudentTable(); });
    } catch (e) {
        stuTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-3">暂无数据</td></tr>';
    }
}

function renderStudentRows(rows) {
    if (!rows.length) {
        stuTableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted py-3">暂无数据</td></tr>';
        return;
    }
    stuTableBody.innerHTML = rows.map(function (r) {
        return '<tr>' +
            '<td>' + r.id + '</td>' +
            '<td>' + r.name + '</td>' +
            '<td>' + (GENDER_TEXT[r.gender] || r.gender) + '</td>' +
            '<td>' + r.age + '</td>' +
            '<td>' + r.teacher_id + '</td>' +
            '<td>' + r.grade + '</td>' +
            '<td>' + formatDate(r.enrollment_date) + '</td>' +
            '<td>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openStudentEdit(' + r.id + ')">修改</button>' +
            '  <button class="btn btn-link btn-sm p-0 text-danger" onclick="removeStudent(' + r.id + ')">删除</button>' +
            '</td>' +
            '</tr>';
    }).join("");
}

/** 加载任课老师下拉选项（全部已有教师），并同步下拉按钮显示 */
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
async function openStudentAdd() {
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["sid"].value = "";
    try {
        await loadTeacherOptions();
    } catch (e) {
        return; /* api 已提示加载失败 */
    }
    syncFormDropdowns(form);
    document.getElementById("editTitle").textContent = "新增学生";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 打开修改弹窗：先查详情回填 */
async function openStudentEdit(id) {
    try {
        const stu = await api("/student/" + id);
        try {
            await loadTeacherOptions();
        } catch (e) {
            return; /* api 已提示加载失败 */
        }
        const form = document.getElementById("editForm");
        form.reset();
        form.elements["sid"].value = stu.id;
        form.elements["name"].value = stu.name;
        form.elements["gender"].value = stu.gender;
        form.elements["age"].value = stu.age;
        form.elements["teacher_id"].value = stu.teacher_id;
        form.elements["grade"].value = stu.grade;
        if (stu.enrollment_date) {
            form.elements["enrollment_date"].value = String(stu.enrollment_date).replace(" ", "T").slice(0, 16);
        }
        syncFormDropdowns(form);
        document.getElementById("editTitle").textContent = "修改学生";
        bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
    } catch (e) { /* api 已提示 */ }
}

/** 提交新增/修改 */
document.getElementById("editForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const f = e.target;
    const id = f.elements["sid"].value;
    const payload = {
        name: f.elements["name"].value.trim(),
        gender: f.elements["gender"].value,
        age: parseInt(f.elements["age"].value, 10),
        teacher_id: parseInt(f.elements["teacher_id"].value, 10),
        grade: f.elements["grade"].value,
        enrollment_date: f.elements["enrollment_date"].value || null,
    };
    try {
        if (id) {
            await api("/student/update/" + id, { method: "PUT", body: payload });
        } else {
            await api("/student/add", { method: "POST", body: payload });
        }
        bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
        showToast(id ? "修改成功" : "新增成功");
        loadStudentTable();
    } catch (e) { /* api 已提示 */ }
});

/** 删除学生 */
async function removeStudent(id) {
    const yes = await confirmDialog("确定删除 ID 为 " + id + " 的学生吗？");
    if (!yes) return;
    try {
        await api("/student/delete/" + id, { method: "DELETE" });
        showToast("删除成功");
        loadStudentTable();
    } catch (e) { /* api 已提示 */ }
}

/** 搜索 */
document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    stuState.keyword = document.getElementById("keyword").value.trim();
    stuState.page = 1;
    loadStudentTable();
});

/** 重置 */
document.getElementById("btnReset").addEventListener("click", function () {
    document.getElementById("keyword").value = "";
    stuState.keyword = "";
    stuState.page = 1;
    loadStudentTable();
});

document.getElementById("btnAdd").addEventListener("click", openStudentAdd);

loadStudentTable();
