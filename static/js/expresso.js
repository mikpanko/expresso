var text = null;
var tokens = null;
var metrics = null;
var tokenMasks = [null, null, null, null, null];
var activeTokenMasks = [false, false, false, false, false];
var modifiedText = false;
var textField = null;
var resultsTable = null;
var analyzeTextButton = null;

$(function(){

    // run at start
    $(document).ready(function() {

        textField = $("#text-entry");
        resultsTable = $("#results-table");
        analyzeTextButton = $("#analyze-text");

        // set navigation bar
        $(".navbar-all").removeClass("active");

        // hide results table
        resultsTable.hide();

        // get rid of active state on the mobile menu button
        $(".navbar-toggle").click(function() {
            $(".navbar-toggle").blur();
        });

        // handle text placeholder behavior
        $("div[data-placeholder]").on("input", function() {
            var el = $(this);
            if (el.text().length) {
                el.removeClass("data-text-empty");
                el.addClass("data-text-filled");
            }
            else {
                el.removeClass("data-text-filled");
                el.addClass("data-text-empty");
                el.html("");
            }
        });

        // strip format when pasting text into text entry field
        textField.on("paste", function() {
            var el = $(this);
            setTimeout(function() {
                el.html(cleanHtml(el.html()));
            }, 10);
        });

        // reset text, tokens, and metrics when text is changed
        textField.on("input", function() {
            text = null;
            tokens = null;
            metrics = null;
            modifiedText = true;
            $(".metric-active").each(function(idx, el){
                el = $(el);
                var classes = el.attr("class");
                if (classes.search("nlp-highlighted-")==-1) {
                    el.removeClass("metric-active");
                }
            });
        });

        // analyze text and display results
        analyzeTextButton.click(function() {

            // get rid of active state on the analysis button
            analyzeTextButton.blur();

            // get text
            //text = html2text(textField.html());
            text = textField.html();
            var hasValidCharacters = false;
            var inputCharacters = textField.text();
            for (var i=0; i<inputCharacters.length; i++) {
                if ((inputCharacters.charCodeAt(i)>=33) && (inputCharacters.charCodeAt(i)<=126)) {
                    hasValidCharacters = true;
                    break;
                }
            }

            if (hasValidCharacters) {

                // put UI in analyzing mode
                analyzeTextButton.button("loading");
                resultsTable.hide();

                // send text to the server for analysis
                $.ajax({
                    type: "POST",
                    url: "/analyze-text",
                    dataType: "json",
                    data: {
                        html: text
                    },
                    success: function(result, textStatus, error) {

                        // success - display analysis results
                        text = result.text;
                        tokens = result.tokens;
                        metrics = result.metrics;
                        addMetricsToResultsTable();
                        textField.html(renderTokensToHtml());
                        resultsTable.show();
                        analyzeTextButton.button('reset');
                        modifiedText = false;
                        $(".metric").addClass("metric-active");

                    },
                    error: function(request, textStatus, error) {

                        // error - display a message
                        alert("Cannot analyze text: " + error);
                    }
                });
            }

        });

        // handle clicking on metrics
        $(".metric").click(function() {
            var el = $(this);

            // only work with active metrics (text hasn't changed since last analysis)
            if (el.hasClass("metric-active")) {
                var classes = el.attr("class");
                if (classes.search("nlp-highlighted-")==-1) {

                    // if metric is not currently highlighted try to turn it on
                    if (activeTokenMasks.indexOf(false)==-1) {

                        // all possible highlights are used on other metrics
                        alert("Used all possible highlights! Please, unselect one before adding another.");

                    } else {

                        // add a highlight
                        var maskNum = activeTokenMasks.indexOf(false);
                        tokenMasks[maskNum] = makeTokenMask(el.attr("id"));
                        textField.html(renderTokensToHtml());
                        activeTokenMasks[maskNum] = true;
                        el.addClass("nlp-highlighted-" + (maskNum+1).toString());

                    }
                } else {

                    // if metric is currently highlighted turn it off
                    var maskNum = parseInt(classes[classes.indexOf("nlp-highlighted-") + 16]) - 1;
                    var className = "nlp-highlighted-" + (maskNum+1).toString();
                    tokenMasks[maskNum] = null;
                    $("span."+className, textField).after("NLP000DELETE");
                    var html = textField.html();
                    var spanRe = new RegExp("<span class=\"" + className + "\">", "mgi");
                    html = html.replace(spanRe, "").replace(/<\/span>NLP000DELETE/mgi, "");
                    textField.html(html);
                    activeTokenMasks[maskNum] = false;
                    el.removeClass(className);
                    if (modifiedText) {
                        el.removeClass("metric-active");
                    }

                }
            }
        });


    });

    // enter metrics into the results table
    function addMetricsToResultsTable() {
        $("#character-count").text(metrics.character_count.toString());
        $("#word-count").text(metrics.word_count.toString());
        $("#vocabulary-size").text(metrics.vocabulary_size.toString());
        $("#sentence-count").text(metrics.sentence_count.toString());
        $("#words-per-sentence").text((Math.round(metrics.words_per_sentence * 10) / 10).toString());
        $("#declarative-ratio").text((Math.round(metrics.declarative_ratio * 1000) / 10).toString() + "%");
        $("#interrogative-ratio").text((Math.round(metrics.interrogative_ratio * 1000) / 10).toString() + "%");
        $("#exclamative-ratio").text((Math.round(metrics.exclamative_ratio * 1000) / 10).toString() + "%");
        $("#stopword-ratio").text((Math.round(metrics.stopword_ratio * 1000) / 10).toString() + "%");
        $("#syllables-per-word").text((Math.round(metrics.syllables_per_word * 10) / 10).toString());
        $("#characters-per-word").text((Math.round(metrics.characters_per_word * 10) / 10).toString());
        $("#readability").text((Math.round(metrics.readability * 10) / 10).toString());
        $("#noun-ratio").text((Math.round(metrics.noun_ratio * 1000) / 10).toString() + "%");
        $("#pronoun-ratio").text((Math.round(metrics.pronoun_ratio * 1000) / 10).toString() + "%");
        $("#verb-ratio").text((Math.round(metrics.verb_ratio * 1000) / 10).toString() + "%");
        $("#adjective-ratio").text((Math.round(metrics.adjective_ratio * 1000) / 10).toString() + "%");
        $("#adverb-ratio").text((Math.round(metrics.adverb_ratio * 1000) / 10).toString() + "%");
        $("#determiner-ratio").text((Math.round(metrics.determiner_ratio * 1000) / 10).toString() + "%");
        $("#other-pos-ratio").text((Math.round(metrics.other_pos_ratio * 1000) / 10).toString() + "%");
        $("#word-freq").html(metrics.word_freq);
        $("#bigram-freq").html(metrics.bigram_freq);
        $("#trigram-freq").html(metrics.trigram_freq);
    }

    // make a mask for highlighting tokens in text
    function makeTokenMask(metric) {
        var mask = [];
        switch (metric) {

            case "metric-stopwords":
                for (var i=0; i<tokens.value.length; i++) {
                    if (tokens.stopword[i]) {
                        mask.push(i);
                    }
                }
                break;

            case "metric-declar-sents":
                var span = [0, null];
                var validSent = ([".", "..."].indexOf(tokens.sentence_end_punctuation[0])>=0);
                for (var i=1; i<tokens.sentence_number.length; i++) {
                    if (tokens.sentence_number[i] != tokens.sentence_number[i-1]) {
                        span[1] = i - 1;
                        if (validSent) {
                            mask.push(span);
                        }
                        span = [i, null];
                        validSent = ([".", "..."].indexOf(tokens.sentence_end_punctuation[i])>=0);
                    }
                }
                span[1] = tokens.sentence_number.length - 1;
                if (validSent) {
                    mask.push(span);
                }
                break;

            case "metric-inter-sents":
                var span = [0, null];
                var validSent = (tokens.sentence_end_punctuation[0]=="?");
                for (var i=1; i<tokens.sentence_number.length; i++) {
                    if (tokens.sentence_number[i] != tokens.sentence_number[i-1]) {
                        span[1] = i - 1;
                        if (validSent) {
                            mask.push(span);
                        }
                        span = [i, null];
                        validSent = (tokens.sentence_end_punctuation[i]=="?");
                    }
                }
                span[1] = tokens.sentence_number.length - 1;
                if (validSent) {
                    mask.push(span);
                }
                break;

            case "metric-exclam-sents":
                var span = [0, null];
                var validSent = (tokens.sentence_end_punctuation[0]=="!");
                for (var i=1; i<tokens.sentence_number.length; i++) {
                    if (tokens.sentence_number[i] != tokens.sentence_number[i-1]) {
                        span[1] = i - 1;
                        if (validSent) {
                            mask.push(span);
                        }
                        span = [i, null];
                        validSent = (tokens.sentence_end_punctuation[i]=="!");
                    }
                }
                span[1] = tokens.sentence_number.length - 1;
                if (validSent) {
                    mask.push(span);
                }
                break;

        }
        return mask;
    }

    // render tokens into an html string
    function renderTokensToHtml() {
        var html = "";

        // reformat token masks into a convenient form
        var spanStartTokens = [];
        var spanEndTokens = [];
        for (var i=0; i<tokenMasks.length; i++) {
            var st = [];
            var en = [];
            if (tokenMasks[i]) {
                for (var j=0; j<tokenMasks[i].length; j++) {
                    if (typeof(tokenMasks[i][j])=="number") {
                        st.push(tokenMasks[i][j]);
                        en.push(tokenMasks[i][j]);
                    } else {
                        st.push(tokenMasks[i][j][0]);
                        en.push(tokenMasks[i][j][1]);
                    }
                }
            }
            spanStartTokens.push(st);
            spanEndTokens.push(en);
        }

        // form html string token by token
        var idxText = 0;
        var idxTokens = 0;
        var token = tokens.value[idxTokens];
        while (idxText<text.length) {

            // add spaces and new lines between tokens
            while ([32, 10, 160].indexOf(text.charCodeAt(idxText))>=0) {
                switch (text[idxText]) {
                    case "\n":
                        html = html + "<br>";
                        break;
                    default:
                        html = html + text[idxText];
                }
                idxText = idxText + 1;
            }

            // add starting points of highlighted spans
            for (var i=0; i<spanStartTokens.length; i++) {
                if (spanStartTokens[i].indexOf(idxTokens)>=0) {
                    html = html + "<span class=\"nlp-highlighted-" + (i+1).toString() + "\">";
                }
            }

            // add token itself
            var tokenInText = null;
            if (["``", "''"].indexOf(token)>=0) {

                // special handling of quotation marks
                if ([34, 171, 187, 8220, 8221, 8222, 8223, 8243, 8246, 12317, 12318].indexOf(text.charCodeAt(idxText))>=0) {
                    tokenInText = text[idxText];
                } else if (["``", "''"].indexOf(text.slice(idxText, idxText+2))>=0) {
                    tokenInText = token;
                } else {
                    console.log(idxText);
                    console.log(text[idxText]);
                    console.log(text.charCodeAt(idxText));
                }
            } else if (token==String.fromCharCode(8230)) {

                // special handling of the symbol '...'
                if (text.charCodeAt(idxText)==8230) {
                    tokenInText = token;
                } else if (text.slice(idxText, idxText+3)=="...") {
                    tokenInText = "...";
                } else {
                    console.log(idxText);
                    console.log(text[idxText]);
                    console.log(text.charCodeAt(idxText));
                }
            } else {

                // all other tokens are displayed as is
                tokenInText = token;
            }
            html = html + tokenInText;
            idxText = idxText + tokenInText.length;

            // add ending points of highlighted spans
            for (var i=0; i<spanEndTokens.length; i++) {
                if (spanEndTokens[i].indexOf(idxTokens)>=0) {
                    html = html + "</span>";
                }
            }

            // prepare the next loop iteration
            idxTokens = idxTokens + 1;
            if (idxTokens<tokens.value.length) {
                token = tokens.value[idxTokens];
            }

        }
        return html;
    }

//    // convert html to text
//    function html2text(htmlStr) {
//        htmlStr = htmlStr.replace(/<div><br><\/div>/mgi, "\n");
//        var el = $("<div>").html(htmlStr);
//        $("div,p,br", el).before("\n");
//        return el.text().trim();
//    }

    // clean html of formatting
    function cleanHtml(htmlStr) {
        var el = $("<div>").html(htmlStr);
        $("div,p,br", el).after("\n");
        $("span.nlp-highlighted", el).before("HIGHLIGHT000START").after("HIGHLIGHT000END");
        return el.text().trim().replace(/\n/mgi, "<br>").replace(/HIGHLIGHT000START/mgi, "<span class=\"nlp-highlighted\">")
            .replace(/HIGHLIGHT000END/mgi, "</span>");
    }

});
