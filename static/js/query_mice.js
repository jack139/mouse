$(function(){
    $('#search').click(function(){
        
        var v_tag = encodeURIComponent($("#v_tag").val());
        var v_house = encodeURIComponent($("#v_house").val());
        var v_uname = encodeURIComponent($("#v_uname").val());
        var v_blood = encodeURIComponent($("#v_blood").val());

        location="/query/mice?v_tag="+v_tag+"&v_house="+v_house+"&v_uname="+v_uname+"&v_blood="+v_blood;
    });
});

