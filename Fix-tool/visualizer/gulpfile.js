const { src, dest, watch, series } = require('gulp');
const concat = require('gulp-concat');

function scripts() {
    return src(['node_modules/jquery/dist/jquery.js','./js/develop.js'])
        .pipe(concat('main.js'))
        .pipe(dest('./js/'));
}

function styles() {
    return src(['node_modules/bootstrap/dist/css/bootstrap.css','./css/develop.css'])
        .pipe(concat('main.css'))
        .pipe(dest('./css/'));
}

function watchAssets(){
    watch(['js/develop.js'], scripts);
    watch(['css/develop.css'], styles);
}

exports.scripts = scripts;
exports.styles = styles;

exports.watch = series(scripts, styles, watchAssets);