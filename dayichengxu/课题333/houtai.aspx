<%@ Page Title="" Language="C#" MasterPageFile="~/MasterPage.master" AutoEventWireup="true" CodeFile="houtai.aspx.cs" Inherits="houtai" %>

<asp:Content ID="Content1" ContentPlaceHolderID="head" Runat="Server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="ContentPlaceHolder1" Runat="Server">
 <div align="center" 
        style="background-image: url('背景图/46b6ed20645eb62030fbd1a504863869.jpg')">
    <asp:GridView ID="GridView1" runat="server" AutoGenerateColumns="False" 
        onrowcancelingedit="GridView1_RowCancelingEdit" 
        onrowdeleting="GridView1_RowDeleting" onrowediting="GridView1_RowEditing" 
        onrowupdating="GridView1_RowUpdating" Width="1036px" 
         
         onrowdatabound="GridView1_RowDataBound">
        <Columns>
            <asp:TemplateField HeaderText="图片">
              
                <ItemTemplate>
                    <asp:Image ID="Image1" runat="server" Width="249px" Height="285px" 
                        ImageUrl='<%# Eval("tupian") %>' />
                </ItemTemplate>
              
            </asp:TemplateField>
            <asp:BoundField DataField="jiage" HeaderText="价格" />
            <asp:BoundField DataField="xinghao" HeaderText="型号" />
            <asp:BoundField DataField="xiangqing" HeaderText="参数" />
            <asp:BoundField DataField="kucun" HeaderText="库存" />
            <asp:CommandField HeaderText="编辑" ShowEditButton="True" />
            <asp:CommandField HeaderText="删除" ShowDeleteButton="True" />
        </Columns>
    
    </asp:GridView></div>
    <div align="center">
     
    <asp:Button ID="Button1" runat="server" onclick="Button1_Click" Text="添加新品" />
    &nbsp;
        <asp:Button ID="Button2" runat="server" onclick="Button2_Click" Text="返回首页" />
    </div>
     
</asp:Content>

