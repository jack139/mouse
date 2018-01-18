$(function(){
    $('#abandon').click(function(){
        var val = [];
        $(':checkbox:checked').each(function(i){
            val[i] = $(this).val();
        });

        if (val.length>0){
            alertify.confirm('请确认', '确定要淘汰所选择的小鼠吗？', 
                function(){ 
                    var house_id = $("#house_id").val();

                    $.ajax({
                        type: "POST",
                        url: "/grp_user/abandon",
                        async: true,
                        timeout: 15000,
                        data: {house_id:house_id,mice:JSON.stringify(val)},
                        dataType: "json",
                        complete: function(xhr, textStatus)
                        {
                            if(xhr.status==200){
                                var retJson = JSON.parse(xhr.responseText);
                                if (retJson["ret"]==0){
                                    alertify.alert('请确认','小鼠淘汰完成！',function(){
                                        location="/grp_user/house_info?house_id="+house_id;
                                    }); 
                                }
                                else{
                                    alertify.error('淘汰小鼠失败!'); 
                                }
                            }
                            else{
                                alertify.error('网络异常!'); 
                            }
                        }
                    });

                }, function(){ });
        }
        else {
            alertify.warning('请选择要淘汰的小鼠!'); 
        }
    });
});

$(function(){
    $('#move').click(function(){
        
        var val = [];
        $(':checkbox:checked').each(function(i){
            val[i] = $(this).val();
        });

        if (val.length>0){
            var target_house_id=$('select[name=target_house_id]').val();

            if (target_house_id==""){
                alertify.warning('请选择要移动到哪个鼠笼!'); 
            }
            else{
                var house_id = $("#house_id").val();

                alertify.confirm('请确认', '确定要移动所选择的小鼠吗？', 
                    function(){ 
                        $.ajax({
                            type: "POST",
                            url: "/grp_user/move",
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
                                            location="/grp_user/house_info?house_id="+house_id;
                                        }); 
                                    }
                                    else{
                                        alertify.error('移动失败!'); 
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


$(function(){
    $('#finish').click(function(){
        
        var house_id = $("#house_id").val();

        alertify.confirm('请确认', '确定结束当前鼠笼的实验吗？', 
            function(){ 
                $.ajax({
                    type: "POST",
                    url: "/grp_user/finish",
                    async: true,
                    timeout: 15000,
                    data: {house_id:house_id},
                    dataType: "json",
                    complete: function(xhr, textStatus)
                    {
                        if(xhr.status==200){
                            var retJson = JSON.parse(xhr.responseText);
                            if (retJson["ret"]==0){
                                alertify.alert('请确认','当前鼠笼实验已结束！鼠笼类型修改为：使用笼',function(){
                                    location="/grp_user/house_info?house_id="+house_id;
                                }); 
                            }
                            else{
                                alertify.error('结束实验失败!'); 
                            }
                        }
                        else{
                            alertify.error('网络异常!'); 
                        }
                    }
                });

            }, function(){ } ); 
    });
});
