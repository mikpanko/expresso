var text = null;
var tokens = null;
var metrics = null;
var tokenMasks = [null, null, null, null, null, null, null, null, null];
var activeTokenMasks = [false, false, false, false, false, false, false, false, false];
var modifiedText = false;
var displaySynonyms = true;
var textField = null;
var textPlaceholder = null;
var expressoPitch = null;
var metricsTables = null;
var metricsElements = null;
var analyzeTextButton = null;
var cleanTextButton = null;
var displaySynonymsButton = null;
var synonymsHoverText = null;
var synonymsMetric = null;
var spinnerContainer = null;
var alertContainer = null;
var wordFreqMetricEl = null;
var bigramFreqMetricEl = null;
var trigramFreqMetricEl = null;

$(function(){

    // run at start
    $(document).ready(function() {

        // find important DOM elements for future use
        textField = $("#text-entry");
        textPlaceholder = $("#text-placeholder");
        expressoPitch = $("#expresso-pitch");
        metricsTables = $("#metrics-tables");
        metricsElements = $("[data-metric]");
        analyzeTextButton = $("#analyze-text");
        cleanTextButton = $("#clean-text");
        displaySynonymsButton = $("#synonyms-button");
        synonymsHoverText = $("#synonyms-hover-text");
        synonymsMetric = $("#synonyms-metric");
        spinnerContainer = $("#spinner-container");
        alertContainer = $("#alert-container");
        wordFreqMetricEl = $("#word-freq");
        bigramFreqMetricEl = $("#bigram-freq");
        trigramFreqMetricEl = $("#trigram-freq");

        // set navigation bar
        $(".navbar-all").removeClass("active");

        // set analyze text button to empty mode
        analyzeTextButton.button("empty");
        setTimeout(function() {
            analyzeTextButton.prop("disabled", true);
        }, 10);

        // hide results table
        metricsTables.hide();

        // set column heights to screensize
        if ($(window).width() >= 992) {
            var columnHeight = $(window).height() - 80;
            $('.column-left').css('height', columnHeight + 'px');
            $('.column-right').css('height', columnHeight + 'px');
        }

        // focus on text field
        textField.focus();

        // add metrics tooltips
        $("[data-metric='weak-verbs']").data("title", '<div class="tooltip-text">overused vague verbs</div>');
        $("[data-metric='filler-words']").data("title", '<div class="tooltip-text">unnecessary words typical for spoken language</div>');
        $("[data-metric='nominalizations']").data("title", '<div class="tooltip-text">complex nouns extended from shorter verbs, adjectives or nouns</div>');
        $("[data-metric='noun-clusters']").data("title", '<div class="tooltip-text">three or more consecutive nouns (and, possibly, "of")</div>');
        $("[data-metric='long-sents']").data("title", '<div class="tooltip-text">&ge;40 words</div>');
        $("[data-metric='short-sents']").data("title", '<div class="tooltip-text">&le;6 words</div>');
        $("[data-metric='entity-substitutions']").data("title", '<div class="tooltip-text">pronouns and vague determiners</div>');
        $("[data-metric='modals']").data("title", '<div class="tooltip-text">verb modifiers signifying ability or necessity</div>');
        $("[data-metric='rare-words']").data("title", '<div class="tooltip-text">not among 5000 most frequent English words</div>');
        $("[data-metric='sents']").data("title", '<div class="tooltip-text">highlighting of the first word in each sentence</div>');
        $("[data-metric='vocabulary-size']").data("title", '<div class="tooltip-text">number of different word stems</div>');
        $("[data-metric='readability']").data("title", '<div class="tooltip-text">comprehension level corresponding to school grade</div>');
        $("[data-metric='declar-sents']").data("title", '<div class="tooltip-text">ending with "." or "..."</div>');
        $("[data-metric='inter-sents']").data("title", '<div class="tooltip-text">ending with "?"</div>');
        $("[data-metric='exclam-sents']").data("title", '<div class="tooltip-text">ending with "!"</div>');
        $("[data-metric='stopwords']").data("title", '<div class="tooltip-text">most common words not carrying text specific information</div>');
        $("#editing-metrics-link").data("title", '<div class="tooltip-text">more information about metrics for editing</div>');
        $("#general-metrics-link").data("title", '<div class="tooltip-text">more information about general metrics</div>');
        cleanTextButton.data("title", '<div class="tooltip-text">useful before copying edited text to paste elsewhere</div>');
        var options = {
            trigger: 'hover',
            placement: 'top',
            html: true,
            delay: { show: 1000, hide: 100 },
            container: 'body'
        };
        metricsElements.tooltip(options);
        $("#editing-metrics-link").tooltip(options);
        $("#general-metrics-link").tooltip(options);
        cleanTextButton.tooltip(options);

        // create loading state spinner
        var spinnerOpts = {
            lines: 13, // The number of lines to draw
            length: 20, // The length of each line
            width: 10, // The line thickness
            radius: 30, // The radius of the inner circle
            corners: 1, // Corner roundness (0..1)
            rotate: 0, // The rotation offset
            direction: 1, // 1: clockwise, -1: counterclockwise
            color: '#808080', // #rgb or #rrggbb or array of colors
            speed: 1, // Rounds per second
            trail: 60, // Afterglow percentage
            shadow: false, // Whether to render a shadow
            hwaccel: false, // Whether to use hardware acceleration
            className: 'spinner', // The CSS class to assign to the spinner
            zIndex: 2e9, // The z-index (defaults to 2000000000)
            top: 'auto', // Top position relative to parent in px
            left: 'auto' // Left position relative to parent in px
        };
        var spinner = new Spinner(spinnerOpts);
        spinnerContainer.hide();

        // get rid of active state on the mobile menu button
        $(".navbar-toggle").on("click", function() {
            $(this).blur();
        });

        // adjust column heights on screen resize
        $(window).resize(function() {
            if ($(this).width() >= 992) {
                var columnHeight = $(window).height() - 80;
                $('.column-left').css('height', columnHeight + 'px');
                $('.column-right').css('height', columnHeight + 'px');
            } else {
                $('.column-left').css('height', '');
                $('.column-right').css('height', '');
            }
        });

        // handle text placeholder and related analyze text button behavior
        textField.on("input", function() {
            if (textField.text().length) {
                textPlaceholder.hide();
                expressoPitch.hide();
                analyzeTextButton.button("reset");
            }
            else {
                textPlaceholder.show();
                expressoPitch.show();
                textField.html("");
                analyzeTextButton.button("empty");
                setTimeout(function() {
                    analyzeTextButton.prop("disabled", true);
                }, 10);
            }
        });

        // strip format when pasting text into text entry field
        textField.on("paste", function() {
            ga('send', 'event', 'text-field', 'paste');
            var el = $(this);
            setTimeout(function() {
                el.html(cleanHtml(el.html()));
            }, 10);
        });

        // reset text, tokens, and metrics when text is changed
        textField.on("input", function() {
            modifiedText = true;
            $(".metric-active").each(function(idx, el) {
                el = $(el);
                var classes = el.attr("class");
                if (classes.search("nlp-highlighted-")==-1) {
                    el.removeClass("metric-active");
                }
            });
        });

        // analyze text and display results
        analyzeTextButton.click(function() {
            var startTime = null;
            var endTime = null;
            var measuredTime = null;
            ga('send', 'event', 'analyze-text', 'click');

            // get rid of active state on the analysis button
            analyzeTextButton.blur();

            // get text
            text = html2text(textField.html());
            var hasValidCharacters = false;
            for (var i=0; i<text.length; i++) {
                if ((text.charCodeAt(i)>=33) && (text.charCodeAt(i)<=126)) {
                    hasValidCharacters = true;
                    break;
                }
            }
            var tooLong = (text.split(" ").length > 5000);

            if (!hasValidCharacters) {

                ga('send', 'event', 'analyze-text', 'invalid-text');
                showAlert("Enter valid English text to analyze.");

            } else if (tooLong) {

                ga('send', 'event', 'analyze-text', 'long-text');
                showAlert("Can only analyze texts less than 5000 words long.");

            } else {

                // put UI in analyzing mode
                analyzeTextButton.button("loading");
                metricsTables.hide();
                $(".metric-active").each(function(idx, el) {
                    el = $(el);
                    removeMetricHighlighting(el);
                });
                $(".metric").removeClass("metric-active");
                spinnerContainer.show();
                spinner.spin(document.getElementById("spinner-container"));

                // send text to the server for analysis
                startTime = new Date().getTime();
                $.ajax({
                    type: "POST",
                    url: "/analyze-text",
                    dataType: "json",
                    data: {
                        html: text
                    },
                    success: function(result, textStatus, error) {

                        // success - display analysis results and add synonym tooltips
                        endTime = new Date().getTime();
                        measuredTime = endTime - startTime;
                        ga('send', 'timing', 'analyze-text-ajax', 'success', measuredTime);
                        ga('send', 'event', 'analyze-text', 'server-success');
                        text = result.text;
                        tokens = result.tokens;
                        metrics = result.metrics;
                        spinner.stop();
                        spinnerContainer.hide();
                        addMetricsToMetricsTables();
                        textField.html(renderTokensToHtml());
                        metricsTables.show();
                        analyzeTextButton.button("complete");
                        setTimeout(function() {
                            analyzeTextButton.prop("disabled", true);
                        }, 10);
                        modifiedText = false;
                        $(".metric").addClass("metric-active");
                        setDisplaySynonyms(true);
                        cleanTextButton.removeClass("active");

                    },
                    error: function(request, textStatus, error) {

                        // error - display a message
                        endTime = new Date().getTime();
                        measuredTime = endTime - startTime;
                        ga('send', 'timing', 'analyze-text-ajax', 'error', measuredTime);
                        ga('send', 'event', 'analyze-text', 'server-error');
                        showAlert("ERROR: Could not analyze text. The website might be overloaded due to high number of visitors. Please, wait couple minutes and try analyzing again.");

                        // reset UI
                        spinner.stop();
                        spinnerContainer.hide();
                        analyzeTextButton.button("reset");

                    }
                });
            }

        });

        // clean text formatting for copy-pasting
        cleanTextButton.click(function() {

            ga('send', 'event', 'clean-text', 'click');

            // get rid of active state on the clean text button
            cleanTextButton.blur();

            $(".metric-active").each(function(idx, el) {
                el = $(el);
                removeMetricHighlighting(el);
            });
            setDisplaySynonyms(false);
            cleanTextButton.addClass("active");
        });

        // handle clicking on synonyms button
        displaySynonymsButton.click(function() {
            ga('send', 'event', 'display-synonyms', 'click');
            if (displaySynonyms) {
                setDisplaySynonyms(false);
            } else {
                setDisplaySynonyms(true);
            }
        });

        // handle clicking on metrics
        $(document).on("click", ".metric", function() {
            var el = $(this);

            // only work with active metrics (text hasn't changed since last analysis)
            if (el.hasClass("metric-active")) {
                var classes = el.attr("class");
                if (classes.search("nlp-highlighted-")==-1) {

                    // if metric is not currently highlighted try to turn it on
                    if (activeTokenMasks.indexOf(false)==-1) {

                        // all possible highlights are used on other metrics
                        showAlert("Used all possible highlights! Please, unselect some before adding more.");

                    } else {

                        // add a highlight and synonym tooltips
                        ga('send', 'event', 'metric', 'click', el.data("metric"));
                        var maskNum = activeTokenMasks.indexOf(false);
                        tokenMasks[maskNum] = makeTokenMask(el.data("metric"), el.data("metric-data"));
                        textField.html(renderTokensToHtml());
                        activeTokenMasks[maskNum] = true;
                        el.addClass("nlp-highlighted-" + (maskNum+1).toString());
                        if (displaySynonyms) {
                            addSynonymTooltips();
                        }
                        cleanTextButton.removeClass("active");

                    }
                } else {

                    // if metric is currently highlighted turn it off
                    removeMetricHighlighting(el);
                    if (displaySynonyms) {
                        addSynonymTooltips();
                    }
                    if (modifiedText) {
                        el.removeClass("metric-active");
                    }

                }
            }
        });

//        $(document).on("dblclick", ".nlp-hover", function() {
//            var el = $(this);
//            var tokenNumStr = el.attr("id").slice(6);
//            var tooltipEl = $("#tooltip-" + tokenNumStr);
//            if (tooltipEl.length > 0) {
//                tooltipEl.parent().parent().remove();
//            } else {
//                el.tooltip("show");
//            }
//        });

    });

    // remove metric highlighting
    function removeMetricHighlighting(el) {
        var classes = el.attr("class");
        if (classes.search("nlp-highlighted-")>=0) {
            var maskNum = parseInt(classes[classes.indexOf("nlp-highlighted-") + 16]) - 1;
            var className = "nlp-highlighted-" + (maskNum+1).toString();
            $("span."+className, textField).after("NLP000DELETE");
            var html = textField.html();
            var spanRe = new RegExp("<span class=\"" + className + "\">", "mgi");
            html = html.replace(spanRe, "").replace(/<\/span>NLP000DELETE/mgi, "");
            textField.html(html);
            tokenMasks[maskNum] = null;
            activeTokenMasks[maskNum] = false;
            el.removeClass(className);
        }
    }

    // add or remove synonym display functionality from text
    function setDisplaySynonyms(val) {
        if (val) {

            // add synonym display functionality
            if (!modifiedText) {
                displaySynonymsButton.removeClass("glyphicon-ban-circle").addClass("glyphicon-ok-circle");
                synonymsHoverText.removeClass("strike-through");
                displaySynonyms = true;
                textField.html(renderTokensToHtml());
                addSynonymTooltips();
                cleanTextButton.removeClass("active");
            }

        } else {

            // remove synonym display functionality
            displaySynonymsButton.removeClass("glyphicon-ok-circle").addClass("glyphicon-ban-circle");
            synonymsHoverText.addClass("strike-through");
            displaySynonyms = false;
            $("span.nlp-hover", textField).after("NLP000DELETE");
            var html = textField.html();
            html = html.replace(/<span class="nlp-hover"[^>]*>/mgi, "").replace(/<\/span>NLP000DELETE/mgi, "");
            textField.html(html);
            removeMetricHighlighting(synonymsMetric);

        }
    }

    // enter metrics into the results table
    function addMetricsToMetricsTables() {
        $("#character-count").text(metrics.character_count.toString());
        $("#word-count").text(metrics.word_count.toString());
        $("#vocabulary-size").text(metrics.vocabulary_size.toString());
        $("#sentence-count").text(metrics.sentence_count.toString());
        $("#words-per-sentence").text((Math.round(metrics.words_per_sentence * 10) / 10).toString());
        if (metrics.std_of_words_per_sentence != -1) {
            $("#std-of-words-per-sentence").text(" \xB1 " + (Math.round(metrics.std_of_words_per_sentence * 10) / 10).toString());
        } else {
            $("#std-of-words-per-sentence").text("");
        }
        $("#long-sentences-ratio").text((Math.round(metrics.long_sentences_ratio * 1000) / 10).toString() + "%");
        $("#short-sentences-ratio").text((Math.round(metrics.short_sentences_ratio * 1000) / 10).toString() + "%");
        $("#declarative-ratio").text((Math.round(metrics.declarative_ratio * 1000) / 10).toString() + "%");
        $("#interrogative-ratio").text((Math.round(metrics.interrogative_ratio * 1000) / 10).toString() + "%");
        $("#exclamative-ratio").text((Math.round(metrics.exclamative_ratio * 1000) / 10).toString() + "%");
        $("#stopword-ratio").text((Math.round(metrics.stopword_ratio * 1000) / 10).toString() + "%");
        if (metrics.syllables_per_word > 0) {
            $("#syllables-per-word").text((Math.round(metrics.syllables_per_word * 10) / 10).toString());
        } else {
            $("#syllables-per-word").text("-");
        }
        $("#characters-per-word").text((Math.round(metrics.characters_per_word * 10) / 10).toString());
        if (metrics.readability > 0) {
            $("#readability").text((Math.round(metrics.readability * 10) / 10).toString());
        } else {
            $("#readability").text("-");
        }
        $("#noun-ratio").text((Math.round(metrics.noun_ratio * 1000) / 10).toString() + "%");
        $("#pronoun-ratio").text((Math.round(metrics.pronoun_ratio * 1000) / 10).toString() + "%");
        $("#verb-ratio").text((Math.round(metrics.verb_ratio * 1000) / 10).toString() + "%");
        $("#adjective-ratio").text((Math.round(metrics.adjective_ratio * 1000) / 10).toString() + "%");
        $("#adverb-ratio").text((Math.round(metrics.adverb_ratio * 1000) / 10).toString() + "%");
        $("#modal-ratio").text((Math.round(metrics.modal_ratio * 1000) / 10).toString() + "%");
        $("#other-pos-ratio").text((Math.round(metrics.other_pos_ratio * 1000) / 10).toString() + "%");
        $("#nominalization-ratio").text((Math.round(metrics.nominalization_ratio * 1000) / 10).toString() + "%");
        $("#weak-verb-ratio").text((Math.round(metrics.weak_verb_ratio * 1000) / 10).toString() + "%");
        $("#entity-substitution-ratio").text((Math.round(metrics.entity_substitution_ratio * 1000) / 10).toString() + "%");
        $("#filler-ratio").text((Math.round(metrics.filler_ratio * 1000) / 10).toString() + "%");
        $("#negation-ratio").text((Math.round(metrics.negation_ratio * 10) / 10).toString());
        $("#noun-cluster-ratio").text((Math.round(metrics.noun_cluster_ratio * 1000) / 10).toString() + "%");
        $("#passive-voice-ratio").text((Math.round(metrics.passive_voice_ratio * 10) / 10).toString());
        $("#rare-word-ratio").text((Math.round(metrics.rare_word_ratio * 1000) / 10).toString() + "%");
        if (metrics.word_freq.length > 0) {
            var freqWordHtml = "";
            for (var i=0; i<Math.min(metrics.word_freq.length, 10); i++) {
                freqWordHtml = freqWordHtml + '<span class="metric" data-metric="word-freq" data-metric-data="' +
                    metrics.word_freq[i][0] + '">' + metrics.word_freq[i][0] + '</span> (' +
                    metrics.word_freq[i][1].toString() + ')<br>';
            }
            wordFreqMetricEl.html(freqWordHtml.slice(0, freqWordHtml.length-4));
        } else {
            wordFreqMetricEl.text("-");
        }
        if (metrics.bigram_freq.length > 0) {
            bigramFreqMetricEl.html("");
            for (var i=0; i<Math.min(metrics.bigram_freq.length, 10); i++) {
                bigramFreqMetricEl.append('<span class="metric" id="tmp-metric">' + metrics.bigram_freq[i][0][0] + ' ' +
                    metrics.bigram_freq[i][0][1] + '</span> (' + metrics.bigram_freq[i][1].toString() +
                    ')');
                $("#tmp-metric").data('metric', 'bigram-freq').data('metric-data', metrics.bigram_freq[i][0]).removeAttr('id');
                if (i < metrics.bigram_freq.length-1) {
                    bigramFreqMetricEl.append('<br>');
                }
            }
        } else {
            bigramFreqMetricEl.text("-");
        }
        if (metrics.trigram_freq.length > 0) {
            trigramFreqMetricEl.html("");
            for (var i=0; i<Math.min(metrics.trigram_freq.length, 10); i++) {
                trigramFreqMetricEl.append('<span class="metric" id="tmp-metric">' + metrics.trigram_freq[i][0][0] +
                    ' ' + metrics.trigram_freq[i][0][1] + ' ' + metrics.trigram_freq[i][0][2] + '</span> (' +
                    metrics.trigram_freq[i][1].toString() + ')');
                $("#tmp-metric").data('metric', 'trigram-freq').data('metric-data', metrics.trigram_freq[i][0]).removeAttr('id');
                if (i < metrics.trigram_freq.length-1) {
                    trigramFreqMetricEl.append('<br>');
                }
            }
        } else {
            trigramFreqMetricEl.text("-");
        }
    }

    // make a mask for highlighting tokens in text
    function makeTokenMask(metric, data) {
        var mask = [];
        switch (metric) {

            case "sents":
                var currSent = 0;
                for (var i=0; i<tokens.values.length; i++) {
                    if ((tokens.sentence_numbers[i] > currSent) && (tokens.number_of_characters[i])) {
                        mask.push(i);
                        currSent = tokens.sentence_numbers[i];
                    }
                }
                break;

            case "long-sents":
                var span = [0, null];
                var wordCount = 0;
                if (tokens.number_of_characters[0]) {
                    wordCount = 1;
                }
                for (var i=1; i<tokens.sentence_numbers.length; i++) {
                    if (tokens.sentence_numbers[i] != tokens.sentence_numbers[i-1]) {
                        span = [span[0], i - 1];
                        if (wordCount >= 40) {
                            mask.push(span);
                        }
                        span = [i, null];
                        wordCount = 0;
                    }
                    if (tokens.number_of_characters[i]) {
                            wordCount = wordCount + 1;
                    }
                }
                span = [span[0], tokens.sentence_numbers.length - 1];
                if (wordCount >= 40) {
                    mask.push(span);
                }
                break;

            case "short-sents":
                var span = [0, null];
                var wordCount = 0;
                if (tokens.number_of_characters[0]) {
                    wordCount = 1;
                }
                for (var i=1; i<tokens.sentence_numbers.length; i++) {
                    if (tokens.sentence_numbers[i] != tokens.sentence_numbers[i-1]) {
                        span = [span[0], i - 1];
                        if (wordCount <= 6) {
                            mask.push(span);
                        }
                        span = [i, null];
                        wordCount = 0;
                    }
                    if (tokens.number_of_characters[i]) {
                            wordCount = wordCount + 1;
                    }
                }
                span = [span[0], tokens.sentence_numbers.length - 1];
                if (wordCount <= 6) {
                    mask.push(span);
                }
                break;

            case "stopwords":
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.stopwords[i]) {
                        mask.push(i);
                    }
                }
                break;

            case "nouns":
                for (var i=0; i<tokens.parts_of_speech.length; i++) {
                    if (tokens.parts_of_speech[i].slice(0, 2)=="NN") {
                        mask.push(i);
                    }
                }
                break;

            case "pronouns":
                for (var i=0; i<tokens.parts_of_speech.length; i++) {
                    if (["PR", "WP", "EX"].indexOf(tokens.parts_of_speech[i].slice(0, 2))>=0) {
                        mask.push(i);
                    }
                }
                break;

            case "verbs":
                for (var i=0; i<tokens.parts_of_speech.length; i++) {
                    if (["VB", "MD"].indexOf(tokens.parts_of_speech[i].slice(0, 2))>=0) {
                        mask.push(i);
                    }
                }
                break;

            case "adjectives":
                for (var i=0; i<tokens.parts_of_speech.length; i++) {
                    if (tokens.parts_of_speech[i].slice(0, 2)=="JJ") {
                        mask.push(i);
                    }
                }
                break;

            case "adverbs":
                for (var i=0; i<tokens.parts_of_speech.length; i++) {
                    if (tokens.parts_of_speech[i].slice(0, 2)=="RB") {
                        mask.push(i);
                    }
                }
                break;

            case "modals":
                for (var i=0; i<tokens.parts_of_speech.length; i++) {
                    if (tokens.parts_of_speech[i].slice(0, 2)=="MD") {
                        mask.push(i);
                    }
                }
                break;

            case "other-pos":
                for (var i=0; i<tokens.parts_of_speech.length; i++) {
                    if ((tokens.number_of_characters[i]) &&
                        (["NN", "PR", "WP", "VB", "JJ", "RB", "MD"].indexOf(tokens.parts_of_speech[i].slice(0, 2))==-1)) {
                        mask.push(i);
                    }
                }
                break;

            case "declar-sents":
                var span = [0, null];
                var validSent = ([".", "..."].indexOf(tokens.sentence_end_punctuations[0])>=0);
                for (var i=1; i<tokens.sentence_numbers.length; i++) {
                    if (tokens.sentence_numbers[i] != tokens.sentence_numbers[i-1]) {
                        span[1] = i - 1;
                        if (validSent) {
                            mask.push(span);
                        }
                        span = [i, null];
                        validSent = ([".", "..."].indexOf(tokens.sentence_end_punctuations[i])>=0);
                    }
                }
                span[1] = tokens.sentence_numbers.length - 1;
                if (validSent) {
                    mask.push(span);
                }
                break;

            case "inter-sents":
                var span = [0, null];
                var validSent = (tokens.sentence_end_punctuations[0]=="?");
                for (var i=1; i<tokens.sentence_numbers.length; i++) {
                    if (tokens.sentence_numbers[i] != tokens.sentence_numbers[i-1]) {
                        span[1] = i - 1;
                        if (validSent) {
                            mask.push(span);
                        }
                        span = [i, null];
                        validSent = (tokens.sentence_end_punctuations[i]=="?");
                    }
                }
                span[1] = tokens.sentence_numbers.length - 1;
                if (validSent) {
                    mask.push(span);
                }
                break;

            case "exclam-sents":
                var span = [0, null];
                var validSent = (tokens.sentence_end_punctuations[0]=="!");
                for (var i=1; i<tokens.sentence_numbers.length; i++) {
                    if (tokens.sentence_numbers[i] != tokens.sentence_numbers[i-1]) {
                        span[1] = i - 1;
                        if (validSent) {
                            mask.push(span);
                        }
                        span = [i, null];
                        validSent = (tokens.sentence_end_punctuations[i]=="!");
                    }
                }
                span[1] = tokens.sentence_numbers.length - 1;
                if (validSent) {
                    mask.push(span);
                }
                break;

            case "nominalizations":
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.nominalizations[i]) {
                        mask.push(i);
                    }
                }
                break;

            case "weak-verbs":
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.weak_verbs[i]) {
                        mask.push(i);
                    }
                }
                break;

            case "entity-substitutions":
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.entity_substitutions[i]) {
                        mask.push(i);
                    }
                }
                break;

            case "filler-words":
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.filler_words[i]) {
                        mask.push(i);
                    }
                }
                break;

            case "negations":
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.negations[i]) {
                        mask.push(i);
                    }
                }
                break;

            case "noun-clusters":
                var span = [null, null];
                var clusterNum = 0;
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.noun_clusters[i] != clusterNum) {
                        if (span[0] != null) {
                            span[1] = i-1;
                            mask.push(span);
                            span = [null, null];
                        }
                        if (tokens.noun_clusters[i]) {
                            span[0] = i;
                            clusterNum = tokens.noun_clusters[i];
                        }
                    }
                }
                break;

            case "passive-voice":
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.passive_voice_cases[i]) {
                        mask.push(i);
                    }
                }
                break;

            case "rare-words":
                for (var i=0; i<tokens.values.length; i++) {
                    if (tokens.expected_word_frequencies[i] == 0) {
                        mask.push(i);
                    }
                }
                break;

            case "synonyms":
                for (var i=0; i<tokens.values.length; i++) {
                    if ((tokens.synonyms[i]) && (tokens.synonyms[i].length > 0)) {
                        mask.push(i);
                    }
                }
                setDisplaySynonyms(true);
                break;

            case "word-freq":
                for (var i=0; i<tokens.stems.length; i++) {
                    if (tokens.stems[i]==data) {
                        mask.push(i);
                    }
                }
                break;

            case "bigram-freq":
                var span = [0, 0];
                var count = 0;
                for (var i=0; i<tokens.stems.length; i++) {
                    if ((count>0) && (tokens.stems[i]==data[count])) {
                        count = count + 1;
                        if (count==2) {
                            span[1] = i;
                            mask.push(span);
                            count = 0;
                            span = [0, 0];
                        }
                    } else if (tokens.stems[i]==data[0]) {
                        count = 1;
                        span[0] = i;
                    } else if (tokens.stems[i]) {
                        count = 0;
                    }
                }
                break;

            case "trigram-freq":
                var span = [0, 0];
                var count = 0;
                for (var i=0; i<tokens.stems.length; i++) {
                    if ((count>0) && (tokens.stems[i]==data[count])) {
                        count = count + 1;
                        if (count==3) {
                            span[1] = i;
                            mask.push(span);
                            count = 0;
                            span = [0, 0];
                        }
                    } else if (tokens.stems[i]==data[0]) {
                        count = 1;
                        span[0] = i;
                    } else if (tokens.stems[i]) {
                        count = 0;
                    }
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
        var token = tokens.values[idxTokens];
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

            // add starting point of synonym span if needed
            if (displaySynonyms && (tokens.synonyms[idxTokens]) && (tokens.synonyms[idxTokens].length > 0)) {
                html = html + "<span class=\"nlp-hover\" id=\"token-" + idxTokens.toString() + "\">";
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

            // add ending point of synonym span if needed
            if (displaySynonyms && (tokens.synonyms[idxTokens]) && (tokens.synonyms[idxTokens].length > 0)) {
                html = html + "</span>";
            }

            // add ending points of highlighted spans
            for (var i=0; i<spanEndTokens.length; i++) {
                if (spanEndTokens[i].indexOf(idxTokens)>=0) {
                    html = html + "</span>";
                }
            }

            // prepare the next loop iteration
            idxTokens = idxTokens + 1;
            if (idxTokens<tokens.values.length) {
                token = tokens.values[idxTokens];
            }

        }

        return html;
    }

    // add synonym tooltips
    function addSynonymTooltips() {
        if (tokens) {
            for (var i=0; i<tokens.values.length; i++) {
                if ((tokens.synonyms[i]) && (tokens.synonyms[i].length > 0)) {
                    var synonymHtml = "<div class=\"tooltip-text\" id=\"tooltip-" + i.toString() + "\">";
                    var synonymNum = Math.min(tokens.synonyms[i].length, 10);
                    for (var j=0; j<(synonymNum-1); j++) {
                        synonymHtml = synonymHtml + tokens.synonyms[i][j] + "<br>";
                    }
                    synonymHtml = synonymHtml + tokens.synonyms[i][synonymNum-1] + "</div>";
                    $("#token-" + i.toString()).data("title", synonymHtml).data("synonymNum", synonymNum);
                }
            }
            var options = {
                trigger: 'hover',
                placement: function() {
                    var el = $(this.$element.context);
                    if (($(window).height() - el.offset().top) > (40 + 25 * el.data("synonymNum"))) {
                        return 'bottom'
                    } else {
                        return 'top'
                    }
                },
                html: true,
                delay: { show: 1000, hide: 100 },
                container: 'body'
            };
            $(".nlp-hover").tooltip(options);
        }
    }

    // convert html to text
    function html2text(htmlStr) {
        htmlStr = htmlStr.replace(/<div><br><\/div>/mgi, "\n").replace(/&nbsp;/mgi, " ");
        var el = $("<div>").html(htmlStr);
        $("div,p,br", el).before("\n");
        return el.text().trim();
    }

    // clean html of formatting
    function cleanHtml(htmlStr) {

        // clean text pasted from MS Word or PDF
        if (($("p.MsoNormal").length > 0) || ($("p.p1").length > 0)) {
            htmlStr = htmlStr.replace(/\n/mgi, " ");
        }

        htmlStr = htmlStr.replace(/<\/div><div><br><\/div>/mgi, "</div>" + "\n").replace(/&nbsp;/mgi, " ");
        var el = $("<div>").html(htmlStr);

        // clean text pasted from PDF further
        $("p.p1", el).each(function() {
            var el1 = $(this);
            el1.after(el1.html());
        });
        $("p.p1", el).remove();

        $("div,p,br", el).after("\n");
        $("span.nlp-highlighted", el).before("HIGHLIGHT000START").after("HIGHLIGHT000END");
        $("span.nlp-hover", el).before("HOVER000START").after("HOVER000END");
        return el.text().trim().replace(/\n/mgi, "<br>").replace(/HIGHLIGHT000START/mgi, "<span class=\"nlp-highlighted\">")
            .replace(/HIGHLIGHT000END/mgi, "</span>").replace(/HOVER000START/mgi, "<span class=\"nlp-hover\">")
            .replace(/HOVER000END/mgi, "</span>");
    }

    // show alert
    function showAlert(alertStr) {
        var alertStartCode = '<div class="alert alert-danger alert-dismissable"><button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>';
        var alertEndCode = '</div>';
        alertContainer.append(alertStartCode + alertStr + alertEndCode);
    }

});
