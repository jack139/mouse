$(function(){
    $('#move').click(function(){
        
        var val = [];
        $(':checkbox:checked').each(function(i){
            val[i] = $(this).val();
        });

        if (val.length>0){
            //var target_house_id=$('select[name=target_house_id]').val();
            var target_house_id=$('input[type=radio][name=target_house_id]:checked').val();

            if (target_house_id==""){
                alertify.warning('请选择要移动到哪个鼠笼!'); 
            }
            else{
                var house_id = $("#house_id").val();

                alertify.confirm('请确认', '确定要移动所选择的小鼠吗？', 
                    function(){ 
                        $.ajax({
                            type: "POST",
                            url: "/grp_admin/move",
                            async: true,
                            timeout: 15000,
                            data: {target_house_id:target_house_id,mice:JSON.stringify(val)},
                            dataType: "json",
                            complete: function(xhr, textStatus)
                            {
                                if(xhr.status==200){
                                    var retJson = JSON.parse(xhr.responseText);
                                    if (retJson["ret"]==0){
                                        alertify.alert('请确认','移动成功!',function(){
                                            location="/grp_admin/house_info?house_id="+house_id;
                                        }); 
                                    }
                                    else{
                                        alertify.error('移动失败：'+retJson["msg"]); 
                                    }
                                }
                                else{
                                    alertify.error('网络异常!'); 
                                }
                            }
                        });

                    }, function(){ }); 
            }
        }   
        else{
            alertify.warning('请选择要移动的小鼠!'); 
        }
    });
});

