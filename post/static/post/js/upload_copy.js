$(function () {

  $(".js-upload-photos").click(function () {
    $("#fileupload").click();
  });
  $(document).on('click','.AddImages',function(){
    //alert();
    var img_id = $(this).attr('img_id');
    var csrf_token = $(this).attr('csrf_token')
    addImages(img_id, csrf_token, );
  });

  $("#fileupload").fileupload({
    dataType: 'json',
    done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
      if (data.result.is_valid) {
        
        var funcEdit = "initImageEditor('" + data.result.url + "', '" + data.result.name + "', " + data.result.id + ");";
        var funcWtEdit = "initWatermarkEditor('" + data.result.url + "', '" + data.result.name + "', " + data.result.id + ");";

        var row = $("<tr>"+
          "<td><i class='fas fa-bars' style='color:#bbb; cursor:move;'></i></td>"+
          "<td>" + data.result.id + "</td>"+
          "<td><a href='" + data.result.url + "'>" + data.result.name + "</a></td>"+
          "<td><img id='image_" + data.result.id + "' style='width:100px; height:100px;' src='" + data.result.url + "'></td>"+
          '<td><button type="button" class="btn btn-primary js-edit-photos" onclick="' + funcEdit + '"><span class="glyphicon glyphicon-cloud-upload"></span>Edit</button></td>' +
          '<td><button type="button" class="btn btn-primary js-edit-watermark" onclick="' + funcWtEdit + '"><span class="glyphicon glyphicon-cloud-upload"></span>Watermark</button></td>' +
          '<td><button type="button" class="btn btn-danger js-delete-photos"><span class="glyphicon glyphicon-cloud-upload"></span>Delete</button></td>'+
          "</tr>").appendTo($("#gallery tbody"));

        var photos = $("#id_photos").val();
        if (photos == "") {
          photos = data.result.id;
        } else {
          photos = photos + "," + data.result.id;
        }
        $("#id_photos").val(photos);

        initRowReordering(row);
        onAfterReordering();
      }
    }
  });

  $("#gallery").on('click', ".js-delete-photos", function () {

    var photos = $("#id_photos").val();
    var id = $(this).closest('tr').find("td:eq(1)").text();

    var photosArr = photos.split(',');
    photosArr = jQuery.grep(photosArr, function(value) {
      return value != id;
    });
    photos = photosArr.join(',');
    $("#id_photos").val(photos);
    $(this).closest('tr').remove();

  });

  var onAfterReordering = function() {

    var photos = "";
    $("#gallery tbody tr").each(function(index, row) {
            if (photos == "") {
                photos = $(row).find("td:eq(1)").text();
            } else {
                photos = photos + "," + $(row).find("td:eq(1)").text();
            }
            //$($(row).find("td").get(1)).html((index + 1) + ".");
        });
        $("#id_photos").val(photos);
  };

    var initRowReordering = function(row) {

        $(row).css("cursor", "move");

        $(row).shieldDraggable({
            helper: function (params) {
                var helper = $('<table class="table table-bordered table-hover"></table>');
                var tbody = $('<tbody />').appendTo(helper);
                tbody.append(row.clone());

                helper.find('td').each(function (index) {
                    $(this).width($(row.find('td')[index]).width());
                });
                helper.width(row.width());

                return helper;
            },

            events: {
                start: function (e) {
                    $(row).addClass("dragged");
                },
                drag: function (e) {
                    var element = $(e.element);
                    var elTopOffset = element.offset().top;

                    var rows = $(row).siblings('tr').not('.dragged').get();

                    for (var i = 0; i < rows.length; i++) {
                        if ($(rows[i]).offset().top > elTopOffset) {
                            $(row).insertBefore($(rows[i]));
                            break;
                        }

                        // if last and still not moved, check if we need to move after
                        if (i >= rows.length - 1) {
                            // move element to the last - after the current
                            $(row).insertAfter($(rows[i]));
                        }
                    }

                },
                stop: function (e) {
                    // dragging has stopped - remove the added classes
                    $(row).removeClass("dragged");
 
                    // cancel the event, so the original element is NOT moved 
                    // to the position of the handle being dragged
                    e.cancelled = true;
                    e.skipAnimation = true;
 
                    // call the on-after-reorder handler function right after this one finishes
                    setTimeout(onAfterReordering, 50);
                }
            },
        });
    };

    var addImages = function(stringImages, csrfToken) {

                var ulElement = document.getElementById(stringImages).parentNode.childNodes[1];
                var children = ulElement.childNodes;
                children.forEach(function(item){
                    if (item.childNodes[0].className.includes('selected')) {
                        imageUrl = item.childNodes[0].childNodes[0].src;

                        $.ajax({
                            type: "POST",
                            url: "/post/uploadFileFromURL/",
                            data: {
                                'url':imageUrl,
                                'csrfmiddlewaretoken': csrfToken 
                            },
                            success: function(result) {
                                if (result.is_valid) {
                                    var funcEdit = "initImageEditor('" + result.url + "', '" + result.name + "', " + result.id + ");";
                                    var funcWtEdit = "initWatermarkEditor('" + result.url + "', '" + result.name + "', " + result.id + ");";

                                    var row = $(
                                        "<tr>"+
                                        "<td><i class='fas fa-bars' style='color:#bbb; cursor:move;'></i></td>"+
                                        "<td>" + result.id + "</td>"+
                                        "<td><a href='" + result.url + "'>" + result.name + "</a></td>"+
                                        "<td><img id='image_" + result.id + "' style='width:100px; height:100px;' src='" + result.url + "'></td>"+
                                        '<td><button type="button" class="btn btn-primary js-edit-photos" onclick="' + funcEdit + '"><span class="glyphicon glyphicon-cloud-upload"></span>Edit</button></td>' +
                                        '<td><button type="button" class="btn btn-primary js-edit-watermark" onclick="' + funcWtEdit + '"><span class="glyphicon glyphicon-cloud-upload"></span>Watermark</button></td>' +
                                        '<td><button type="button" class="btn btn-danger js-delete-photos"><span class="glyphicon glyphicon-cloud-upload"></span>Delete</button></td>'+
                                        "</tr>"
                                    ).appendTo($("#gallery tbody"));

                                    var photos = $("#id_photos").val();
                                    if (photos == "") {
                                        photos = result.id;
                                    } else {
                                        photos = photos + "," + result.id;
                                    }
                                    $("#id_photos").val(photos);
                                    $('#ragicModal').modal('hide');

                                    initRowReordering(row);
                                    onAfterReordering();

                                }
                            },
                            error: function(err) {
                              alert(err);
                            } 
                        });
                    }
                });
    }

    $("#gallery tbody tr").each(function () {
        initRowReordering($(this));
    });

  $(".js-upload-videos").click(function () {
    $("#videoupload").click();
  });

  $("#videoupload").fileupload({
    dataType: 'json',
    done: function (e, data) {  /* 3. PROCESS THE RESPONSE FROM THE SERVER */
      if (data.result.is_valid) {
        
        $("#videoList tbody").prepend(
          "<tr>"+
          "<td>" + data.result.id + "</td>"+
          "<td><a href='" + data.result.url + "'>" + data.result.name + "</a></td>"+
          "<td><video id='video_" + data.result.id + "' style='width:100px; height:100px;' src='" + data.result.url + "'></td>"+
          '<td><button type="button" class="btn btn-primary js-delete-videos"><span class="glyphicon glyphicon-cloud-upload"></span>Delete</button></td>'+
          "</tr>"
        );

        var videos = $("#id_videos").val();
        if (videos == "") {
          videos = data.result.id;
        } else {
          videos = videos + "," + data.result.id;
        }
        $("#id_videos").val(videos);
      }
    }
  });

  $("#videoList").on('click', ".js-delete-video", function () {

    var videos = $("#id_videos").val();
    var id = $(this).closest('tr').find("td:eq(0)").text();

    var videosArr = videos.split(',');
    videosArr = jQuery.grep(videosArr, function(value) {
      return value != id;
    });
    videos = videosArr.join(',');
    $("#id_videos").val(videos);
    $(this).closest('tr').remove();

  });


});