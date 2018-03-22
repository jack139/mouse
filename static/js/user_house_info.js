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
                                    alertify.error('淘汰小鼠失败：'+retJson["msg"]); 
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
                                alertify.error('结束实验失败：'+retJson["msg"]); 
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


$(function(){
    $('#newborn').click(function(){
        
        var house_id = $("#house_id").val();

        alertify.prompt2('请输入',
            function(evt, value, value2){ 
                alertify.success(value2);

                $.ajax({
                    type: "POST",
                    url: "/grp_user/newborn",
                    async: true,
                    timeout: 15000,
                    data: {house_id:house_id, num:value},
                    dataType: "json",
                    complete: function(xhr, textStatus)
                    {
                        if(xhr.status==200){
                            var retJson = JSON.parse(xhr.responseText);
                            if (retJson["ret"]==0){
                                alertify.alert('请确认','新生小鼠已添加！',function(){
                                    location="/grp_user/house_info?house_id="+house_id;
                                }); 
                            }
                            else{
                                alertify.error('添加新生小鼠失败：'+retJson['msg']); 
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




alertify.dialog('prompt2', function () {
    var input = document.createElement('INPUT');
    var input2 = document.createElement('INPUT');
    var p = document.createElement('P');
    var p2 = document.createElement('P');

    function clearContents(element){
        while (element.lastChild) {
            element.removeChild(element.lastChild);
        }
    }

    return {
        main: function (_title, _onok, _oncancel) {
            var title, message, value, onok, oncancel;

            title = _title;
            message = "新生小鼠数量";
            message2 = "出生日期（格式：yyyymmdd）";
            value = '';
            onok = _onok;
            oncancel = _oncancel;

            this.set('title', title);
            this.set('message', message);
            this.set('value', value);
            this.set('onok', onok);
            this.set('oncancel', oncancel);
            return this;
        },
        setup: function () {
            return {
                buttons: [
                    {
                        text: alertify.defaults.glossary.ok,
                        key: 13,
                        className: alertify.defaults.theme.ok,
                    },
                    {
                        text: alertify.defaults.glossary.cancel,
                        key: 27,
                        invokeOnClose: true,
                        className: alertify.defaults.theme.cancel,
                    }
                ],
                focus: {
                    element: input,
                    select: true
                },
                options: {
                    maximizable: false,
                    resizable: false
                }
            };
        },
        build: function () {
            input.className = alertify.defaults.theme.input;
            input.setAttribute('type', 'text');
            input.value = this.get('value');
            input2.className = alertify.defaults.theme.input;
            input2.setAttribute('type', 'text');
            input2.value = this.get('value');
            this.elements.content.appendChild(p);
            this.elements.content.appendChild(input);
            this.elements.content.appendChild(p2);
            this.elements.content.appendChild(input2);
        },
        prepare: function () {
            //nothing
        },
        setMessage: function (message) {
            clearContents(p);
            p.innerHTML = "新生小鼠数量";
            p2.innerHTML = "出生日期（格式：yyyymmdd）";
        },
        settings: {
            message: undefined,
            labels: undefined,
            onok: undefined,
            oncancel: undefined,
            value: '',
            type:'text',
            reverseButtons: undefined,
        },
        settingUpdated: function (key, oldValue, newValue) {
            switch (key) {
            case 'message':
                this.setMessage(newValue);
                break;
            case 'value':
                input.value = newValue;
                break;
            case 'type':
                input.type = 'text';
                break;
            }
        },
        callback: function (closeEvent) {
            var returnValue;
            switch (closeEvent.index) {
            case 0:
                this.settings.value = input.value;
                if (typeof this.get('onok') === 'function') {
                    returnValue = this.get('onok').call(this, closeEvent, this.settings.value, input2.value);
                    if (typeof returnValue !== 'undefined') {
                        closeEvent.cancel = !returnValue;
                    }
                }
                break;
            case 1:
                if (typeof this.get('oncancel') === 'function') {
                    returnValue = this.get('oncancel').call(this, closeEvent);
                    if (typeof returnValue !== 'undefined') {
                        closeEvent.cancel = !returnValue;
                    }
                }
                if(!closeEvent.cancel){
                    input.value = this.settings.value;
                }
                break;
            }
        }
    };
});