$(function(){

    // run at start
    $(document).ready(function(){

        // hide results table
        $("#results-table").hide();

    });

    // analyze text and display results
    $("#analyze-text").click(function(){

        // get text
        var text = $("#text-entry").val();

        if (text) {
            // send text to the server
            $.ajax({
                type: "POST",
                url: "/analyze-text",
                dataType: "json",
                data: {
                    text: text
                },
                success: function(result, textStatus, error) {
                    // display analysis results
                    console.log(result);
                    $("#word-count").text(result.word_count.toString());
                    $("#vocabulary-size").text(result.vocabulary_size.toString());
                    $("#sentence-count").text(result.sentence_count.toString());
                    $("#declarative-ratio").text(Math.round(result.declarative_ratio * 100).toString() + "%");
                    $("#interrogative-ratio").text(Math.round(result.interrogative_ratio * 100).toString() + "%");
                    $("#exclamative-ratio").text(Math.round(result.exclamative_ratio * 100).toString() + "%");
                    $("#results-table").show();
                },
                error: function(request, textStatus, error) {
                    alert("Cannot analyze text!");
                }
            });
        };

    });

});
