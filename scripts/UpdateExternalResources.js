console.log("开始更新远程外部资源");

$httpAPI("POST", "/v1/external_resources/update", { key: "all" }, function (result) {
  console.log("外部资源更新结果：" + JSON.stringify(result));
  $done();
});
