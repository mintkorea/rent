components.html("""
<script>
document.addEventListener("keydown", function(e) {
    if (e.key === "ArrowLeft") {
        window.location.search = "?nav=prev";
    }
    if (e.key === "ArrowRight") {
        window.location.search = "?nav=next";
    }
});
</script>
""", height=0)