/**
 * 通知公告页面逻辑（纯前端模拟：数据存 localStorage，无后端接口）
 * 数据读写使用 common.js 中的 loadNotices/saveNotices，与首页"最新公告"卡片共用
 */
const noticeState = { keyword: "" };
const noticeTableBody = document.getElementById("tableBody");
let noticeList = loadNotices();

/** 渲染公告列表（按发布时间倒序，支持标题/发布人过滤） */
function renderNoticeTable() {
    let rows = noticeList.slice();
    if (noticeState.keyword) {
        const kw = noticeState.keyword;
        rows = rows.filter(function (n) {
            return n.title.indexOf(kw) !== -1 || n.publisher.indexOf(kw) !== -1;
        });
    }
    rows.sort(function (a, b) { return b.publish_time.localeCompare(a.publish_time); });
    document.getElementById("totalInfo").textContent = "共 " + rows.length + " 条";
    if (!rows.length) {
        noticeTableBody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-3">暂无数据</td></tr>';
        return;
    }
    noticeTableBody.innerHTML = rows.map(function (n) {
        return '<tr>' +
            '<td>' + n.id + '</td>' +
            '<td>' + n.title + '</td>' +
            '<td>' + n.publisher + '</td>' +
            '<td>' + n.publish_time + '</td>' +
            '<td>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openNoticeDetail(' + n.id + ')">详情</button>' +
            '  <button class="btn btn-link btn-sm p-0 me-2" onclick="openNoticeEdit(' + n.id + ')">修改</button>' +
            '  <button class="btn btn-link btn-sm p-0 text-danger" onclick="removeNotice(' + n.id + ')">删除</button>' +
            '</td>' +
            '</tr>';
    }).join("");
}

/** 打开新增弹窗 */
function openNoticeAdd() {
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["nid"].value = "";
    document.getElementById("editTitle").textContent = "新增公告";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 打开修改弹窗 */
function openNoticeEdit(id) {
    const n = noticeList.filter(function (x) { return x.id === id; })[0];
    if (!n) return;
    const form = document.getElementById("editForm");
    form.reset();
    form.elements["nid"].value = n.id;
    form.elements["title"].value = n.title;
    form.elements["publisher"].value = n.publisher;
    form.elements["content"].value = n.content;
    document.getElementById("editTitle").textContent = "修改公告";
    bootstrap.Modal.getOrCreateInstance(document.getElementById("editModal")).show();
}

/** 提交新增/修改（发布时间：新增取当前时间，修改保持不变） */
document.getElementById("editForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const f = e.target;
    const id = f.elements["nid"].value;
    const title = f.elements["title"].value.trim();
    const publisher = f.elements["publisher"].value.trim();
    const content = f.elements["content"].value.trim();
    if (id) {
        const n = noticeList.filter(function (x) { return String(x.id) === id; })[0];
        if (n) {
            n.title = title;
            n.publisher = publisher;
            n.content = content;
        }
        showToast("修改成功");
    } else {
        const nextId = noticeList.reduce(function (m, x) { return Math.max(m, x.id); }, 0) + 1;
        noticeList.push({
            id: nextId, title: title, publisher: publisher,
            content: content, publish_time: noticeNowText(),
        });
        showToast("新增成功");
    }
    saveNotices(noticeList);
    bootstrap.Modal.getInstance(document.getElementById("editModal")).hide();
    renderNoticeTable();
});

/** 查看详情弹窗 */
function openNoticeDetail(id) {
    const n = noticeList.filter(function (x) { return x.id === id; })[0];
    if (!n) return;
    document.getElementById("dTitle").textContent = n.title;
    document.getElementById("dMeta").textContent = "发布人：" + n.publisher + "　发布时间：" + n.publish_time;
    document.getElementById("dContent").textContent = n.content;
    bootstrap.Modal.getOrCreateInstance(document.getElementById("detailModal")).show();
}

/** 删除公告 */
async function removeNotice(id) {
    const yes = await confirmDialog("确定删除该公告吗？");
    if (!yes) return;
    noticeList = noticeList.filter(function (x) { return x.id !== id; });
    saveNotices(noticeList);
    showToast("删除成功");
    renderNoticeTable();
}

/** 搜索 */
document.getElementById("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    noticeState.keyword = document.getElementById("keyword").value.trim();
    renderNoticeTable();
});

/** 重置 */
document.getElementById("btnReset").addEventListener("click", function () {
    document.getElementById("keyword").value = "";
    noticeState.keyword = "";
    renderNoticeTable();
});

document.getElementById("btnAdd").addEventListener("click", openNoticeAdd);

renderNoticeTable();
