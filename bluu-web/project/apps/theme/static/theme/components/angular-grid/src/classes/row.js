/// <reference path="../../lib/jquery-1.8.2.min" />
/// <reference path="../../lib/angular.js" />
/// <reference path="../constants.js" />
/// <reference path="../namespace.js" />
/// <reference path="../navigation.js" />
/// <reference path="../utils.js" />
ng.Row = function(entity, config, selectionService) {
    var self = this, // constant for the selection property that we add to each data item
        canSelectRows = config.canSelectRows;

    self.jqueryUITheme = config.jqueryUITheme;
    self.rowClasses = config.rowClasses;
    self.entity = entity;
    self.modelIndex = 0;
    self.selectionService = selectionService;
	self.selected = null;
    self.cursor = canSelectRows ? 'pointer' : 'default';
	self.setSelection = function(isSelected) {
		self.selectionService.setSelection(self, isSelected);
		self.selectionService.lastClickedRow = self;
	};
    self.continueSelection = function(event) {
        self.selectionService.ChangeSelection(self, event);
    };
    self.toggleSelected = function(event) {
        if (!canSelectRows && !config.enableCellSelection) {
            return true;
        }
        var element = event.target || event;
        //check and make sure its not the bubbling up of our checked 'click' event 
        if (element.type == "checkbox" && element.parentElement.className != "ngSelectionCell ng-scope") {
            return true;
        }
        if (config.selectWithCheckboxOnly && element.type != "checkbox") {
            return true;
        } else {
            if (self.beforeSelectionChange(self, event)) {
                self.continueSelection(event);
                return self.afterSelectionChange(self, event);
            }
        }
        return false;
    };
    self.rowIndex = 0;
    self.offsetTop = function() {
        return self.rowIndex * config.rowHeight;
    };
    self.rowDisplayIndex = 0;
    self.alternatingRowClass = function () {
        var isEven = (self.rowIndex % 2) === 0;
        var classes = {
            'selected': self.selected,
            'ui-state-default': self.jqueryUITheme && isEven,
            'ui-state-active': self.jqueryUITheme && !isEven,
            'even': isEven,
            'odd': !isEven
        };
        return classes;
    };
    self.beforeSelectionChange = config.beforeSelectionChangeCallback;
    self.afterSelectionChange = config.afterSelectionChangeCallback;

    self.getProperty = function(path) {
        return ng.utils.evalProperty(self.entity, path);
    };
};