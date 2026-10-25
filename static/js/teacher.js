/**
 * 教师管理页面逻辑
 * 接口：GET /teacher/list（无后端分页，前端过滤+切片）、POST /teacher/add、
 *       PUT /teacher/update/{id}、DELETE /teacher/delete/{id}、GET /teacher/{id}/detail
 */
const GENDER_TEXT = { man: "男", woman: "女" };

const teaState = { page: 1, size: 10, keyword: "", all: [] };
const teaTableBody = document.getElementById("tableBody");

/** 加载教师列表（前端分页） */
async function loadTeacherTable() {
    try {
        const list = await api("/teacher/list");
        const all = list || [];
        teaState.all = teaState.keyword
            ? all.filter(function (t) { return t.name.indexOf(teaState.keyword) !== -1; })
            : all;
        const total = teaState.all.length;
        const rows = teaState.all.slice((teaState.page - 1) * teaState.size, teaState.page * teaState.size);
        renderTeacherRows(rows);
        document.getElementById("totalInfo").textContent = "共 " + total + " 条";
        renderPagination(document.getElementById("pagination"), total, teaState.page, teaState.size,
            function (p) { teaState.page = p; renderTeacherPage(); });
    } catch (e) {
        teaTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">暂无数据</td></tr>';
    }
}

/** 翻页时对已加载的数据重新切片，避免重复请求 */
function renderTeacherPage() {
    const rows = teaState.all.slice((teaState.page - 1) * teaState.size, teaState.page * teaState.size);
    renderTeacherRows(rows);
    renderPagination(document.getElementById("pagination"), teaState.all.length, teaState.page, teaState.size,
        function (p) { teaState.page = p; renderTeacherPage(); });
}

function renderTeacherRows(rows) {
    if (!rows.length) {
        teaTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">暂无数据</td></tr>';
        return;
    }
    teaTableBody.innerHTML = rows.map(function (r) {
        return '<tr>' +
            '<td>' + r.id + '</td>' +
            '<td>' + r.name + '</td>' +
            '<td>' + (GENDER_TEXT[r.gender] || r.gender) + '</td>' +
            '<td>' + r.age + '</td>' +
            '<td>' + r.subject + '</td>' +
            '<td>' + (r.phone || "-") + '</td>' +
            '<td>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="viewStudents(' + r.id + ')">学生</button>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openTeacherEdit(' + r.id + ')">修改</button>' +
            '  <button class="btn btn-link btn-sm p-0 text-danger" onclick="removeTeacher(' + r.id + ')">删除</button>' +
            '</td>' +
            '</tr>';
    }).join("");
}

/** 查看某教师名下的学生（走本地组装接口，不触发远程伙伴调用） */
async function viewStudents(id) {
    try {
        const detail = await api("/teacher/" + id + "/detail");
        const students = detail.students || [];
        document.getElementById("stuModalTitle").textContent =
            "教师【" + detail.name + "】的学生（共 " + detail.student_count + " 人）";
        document.getElementById("stuTableBody").innerHTML = students.length
            ? students.map(function (s) {
                return '<tr>' +
                    '<td>' + s.id + '</td>' +
                    '<td>' + s.name + '</td>' +
                    '<td>' + (GENDER_TEXT[s.gender] || s.gender) + '</td>' +
                    '<td>' + s.age + '</td>' +
                    '<td>' + s.grade + '</td>' +
                    '</tr>';
            }).join("")
            : '<tr><td colspan="5" class="text-center text-muted py-3">该教师暂无学生</td></tr>';
        bootstrap.Modal.getOrCreateInstance(document.getElementById("stuModal")).show();
    } catch (e) { /* api 已提示 */ }
}

/** 打开新增弹窗 */
function openTeacherAdd() {
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["tid"].value = "";
    syncFormDropdowns(form);
    document.getElementById("editTitle").textContent = "新增教师";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 打开修改弹窗 */
function openTeacherEdit(id) {
    const tea = teaState.all.filter(function (t) { return t.id === id; })[0];
    if (!tea) return;
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["tid"].value = tea.id;
    form.elements["name"].value = tea.name;
    form.elements["gender"].value = tea.gender;
    form.elements["age"].value = tea.age;
    form.elements["subject"].value = tea.subject;
    form.elements["phone"].value = tea.phone || "";
    syncFormDropdowns(form);
    document.getElementById("editTitle").textContent = "修改教师";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 提交新增/修改 */
document.getElementById("editForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const f = e.target;
    const id = f.elements["tid"].value;
    const payload = {
        name: f.elements["name"].value.trim(),
        gender: f.elements["gender"].value,
        age: parseInt(f.elements["age"].value, 10),
        subject: f.elements["subject"].value.trim(),
        phone: f.elements["phone"].value.trim() || null,
    };
    try {
        if (id) {
            await api("/teacher/update/" + id, { method: "PUT", body: payload });
        } else {
            await api("/teacher/add", { method: "POST", body: payload });
        }
        bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
        showToast(id ? "修改成功" : "新增成功");
        loadTeacherTable();
    } catch (e) { /* api 已提示 */ }
});

/** 删除教师 */
async function removeTeacher(id) {
    const yes = await confirmDialog("确定删除 ID 为 " + id + " 的教师吗？");
    if (!yes) return;
    try {
        await api("/teacher/delete/" + id, { method: "DELETE" });
        showToast("删除成功");
        loadTeacherTable();
    } catch (e) { /* api 已提示 */ }
}

/** 搜索 */
document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    teaState.keyword = document.getElementById("keyword").value.trim();
    teaState.page = 1;
    loadTeacherTable();
});

/** 重置 */
document.getElementById("btnReset").addEventListener("click", function () {
    document.getElementById("keyword").value = "";
    teaState.keyword = "";
    teaState.page = 1;
    loadTeacherTable();
});

document.getElementById("btnAdd").addEventListener("click", openTeacherAdd);

loadTeacherTable();
